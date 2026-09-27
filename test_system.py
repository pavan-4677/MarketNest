import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketnest.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from marketplace.models import Product, Category, Favorite, ContactMessage
from django.core.files.uploadedfile import SimpleUploadedFile

def run_tests():
    c = Client()

    # 1. Test Login
    logged_in = c.login(username='rahul', password='demo12345')
    assert logged_in, 'Login failed for rahul'
    print("[OK] rahul login successful")

    # 2. Test Dashboard
    resp = c.get('/dashboard/')
    assert resp.status_code == 200, f'Dashboard failed: {resp.status_code}'
    assert b'Welcome, Rahul' in resp.content or b'Welcome, rahul' in resp.content
    print("[OK] Dashboard loaded for authenticated user")

    # 3. Test Create Listing
    cat = Category.objects.first()
    # 1x1 GIF bytes
    gif_bytes = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    test_image = SimpleUploadedFile('test_phone.png', gif_bytes, content_type='image/png')

    create_resp = c.post('/listing/new/', {
        'title': 'Automated Test iPhone 13 Pro',
        'category': cat.id,
        'price': '35000',
        'condition': 'LIKE_NEW',
        'location': 'Indiranagar, Bengaluru',
        'description': 'Automated test product created via Django client.',
        'image': test_image,
    })
    assert create_resp.status_code == 302, f'Create listing failed: {create_resp.status_code}'
    created_product = Product.objects.filter(title='Automated Test iPhone 13 Pro').first()
    assert created_product is not None, 'Product not found in DB'
    assert created_product.seller.username == 'rahul', 'Seller mismatch'
    print(f"[OK] Create listing successful! ID={created_product.id}")

    # 4. Test Edit Listing
    edit_resp = c.post(f'/listing/{created_product.id}/edit/', {
        'title': 'Automated Test iPhone 13 Pro (Updated)',
        'category': cat.id,
        'price': '34000',
        'condition': 'GOOD',
        'location': 'Indiranagar, Bengaluru',
        'description': 'Updated description.',
    })
    assert edit_resp.status_code == 302, f'Edit listing failed: {edit_resp.status_code}'
    created_product.refresh_from_db()
    assert created_product.title == 'Automated Test iPhone 13 Pro (Updated)', 'Title not updated'
    assert created_product.price == 34000, 'Price not updated'
    print("[OK] Edit listing successful!")

    # 5. Test Toggle Status (Mark as Sold / Active)
    toggle_resp = c.post(f'/listing/{created_product.id}/toggle-status/')
    assert toggle_resp.status_code == 302
    created_product.refresh_from_db()
    assert created_product.is_active is False, 'Status not toggled to False'
    print("[OK] Toggle listing status (Mark as sold) successful!")

    # 6. Test Delete Listing
    del_resp = c.post(f'/listing/{created_product.id}/delete/')
    assert del_resp.status_code == 302
    assert not Product.objects.filter(id=created_product.id).exists(), 'Product not deleted'
    print("[OK] Delete listing successful!")

    # 7. Test Toggle Favorite (AJAX)
    prod1 = Product.objects.first()
    fav_resp = c.post(f'/product/{prod1.id}/favorite/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert fav_resp.status_code == 200, f'Favorite failed: {fav_resp.status_code}'
    fav_data = fav_resp.json()
    assert 'is_favorited' in fav_data, 'Favorite response invalid'
    print(f"[OK] Favorite toggle AJAX successful! is_favorited={fav_data['is_favorited']}")

    # 8. Test Inquiry message to another seller
    priya_prod = Product.objects.filter(seller__username='priya').first()
    inquiry_resp = c.post(f'/product/{priya_prod.id}/', {
        'message': 'Hi Priya, automated inquiry test!',
        'sender_phone': '+91 99999 88888',
    })
    assert inquiry_resp.status_code == 302, f'Inquiry failed: {inquiry_resp.status_code}'
    msg_obj = ContactMessage.objects.filter(sender__username='rahul', receiver__username='priya', product=priya_prod).first()
    assert msg_obj is not None, 'Inquiry message not saved in DB'
    print("[OK] Contact seller inquiry message successfully saved in DB!")

    # 9. Test Registration (requires logged-out state)
    c.logout()
    reg_resp = c.post('/register/', {
        'username': 'newuser1',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newuser1@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
    })
    assert reg_resp.status_code == 302, f'Register failed: {reg_resp.status_code}'
    assert User.objects.filter(username='newuser1').exists(), 'New user not found in DB'
    print("[OK] User registration and auto-login successful!")

    # 10. Test Search & Filter Query
    search_resp = c.get('/browse/?q=Galaxy&category=mobiles&sort=price_asc')
    assert search_resp.status_code == 200
    assert b'Samsung Galaxy S23' in search_resp.content
    print("[OK] Search and Category filter query successful!")

    print("\n========================================================")
    print("ALL 10 VERIFICATION TESTS PASSED PERFECTLY!")
    print("========================================================\n")

if __name__ == '__main__':
    run_tests()
