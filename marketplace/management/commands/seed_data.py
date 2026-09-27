import os
from pathlib import Path
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from marketplace.models import Category, Product, ProductImage, Favorite, ContactMessage, Profile

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def create_product_banner(file_path, title, category_name, price_str, bg_color=(15, 118, 110)):
    """Generate an attractive real product image file on disk using Pillow."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not HAS_PIL:
        # Fallback empty byte file if Pillow not available
        with open(file_path, 'wb') as f:
            f.write(b'')
        return

    width, height = 800, 600
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Subtle inner gradient rectangle
    inner_margin = 30
    draw.rectangle(
        [(inner_margin, inner_margin), (width - inner_margin, height - inner_margin)],
        outline=(255, 255, 255, 40),
        width=2
    )

    # Category badge background
    badge_x, badge_y = 60, 60
    draw.rounded_rectangle([(badge_x, badge_y), (badge_x + 220, badge_y + 44)], radius=8, fill=(255, 255, 255, 230))
    
    # Text drawing
    # Fallback to default font if custom font not available
    try:
        font_large = ImageFont.load_default(size=36)
        font_title = ImageFont.load_default(size=44)
        font_sub = ImageFont.load_default(size=24)
        font_badge = ImageFont.load_default(size=20)
    except Exception:
        font_large = font_title = font_sub = font_badge = ImageFont.load_default()

    # Draw Category Badge text
    draw.text((badge_x + 16, badge_y + 12), category_name.upper(), fill=(15, 23, 42), font=font_badge)

    # MarketNest watermark
    draw.text((width - 240, 70), "MARKETNEST VERIFIED", fill=(220, 240, 235), font=font_badge)

    # Wrap title into 2 lines if long
    words = title.split()
    line1 = " ".join(words[:4])
    line2 = " ".join(words[4:]) if len(words) > 4 else ""

    draw.text((60, 220), line1, fill=(255, 255, 255), font=font_title)
    if line2:
        draw.text((60, 280), line2, fill=(255, 255, 255), font=font_title)

    # Price pill
    draw.rounded_rectangle([(60, 420), (320, 500)], radius=12, fill=(245, 158, 11))
    draw.text((85, 442), f"Rs. {price_str}", fill=(15, 23, 42), font=font_large)

    # Tagline footer
    draw.text((60, 530), "MarketNest - Buy Local. Sell Smart.", fill=(200, 230, 225), font=font_sub)

    img.save(file_path, 'JPEG', quality=88)


class Command(BaseCommand):
    help = 'Seeds database with realistic demo users, categories, products, favorites, and inquiries'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- Starting MarketNest Database Seeding ---"))

        # 1. Superuser
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@marketnest.com',
                'first_name': 'Admin',
                'last_name': 'MarketNest',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created or not admin_user.check_password('admin123'):
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("[OK] Superuser 'admin' created/updated (password: admin123)"))

        # 2. Demo Users
        demo_users_data = [
            {
                'username': 'rahul',
                'email': 'rahul@example.com',
                'first_name': 'Rahul',
                'last_name': 'Sharma',
                'location': 'Indiranagar, Bengaluru',
                'phone': '+91 98451 23456',
                'bio': 'Tech enthusiast, software developer, and gadget collector. Always maintaining devices in immaculate condition.',
            },
            {
                'username': 'priya',
                'email': 'priya@example.com',
                'first_name': 'Priya',
                'last_name': 'Patel',
                'location': 'Bandra West, Mumbai',
                'phone': '+91 98200 98765',
                'bio': 'Interior decor enthusiast & home stylist. Moving to a new flat, selling well-cared-for home and study essentials.',
            },
            {
                'username': 'arjun',
                'email': 'arjun@example.com',
                'first_name': 'Arjun',
                'last_name': 'Verma',
                'location': 'Connaught Place, Delhi',
                'phone': '+91 98111 54321',
                'bio': 'Fitness trainer and cycling enthusiast. Selling verified sports equipment and outdoor travel essentials.',
            },
            {
                'username': 'sneha',
                'email': 'sneha@example.com',
                'first_name': 'Sneha',
                'last_name': 'Reddy',
                'location': 'Jubilee Hills, Hyderabad',
                'phone': '+91 98765 11223',
                'bio': 'Fashion designer and visual artist. Curating sustainable pre-loved wardrobe items and camera gear.',
            }
        ]

        users_dict = {}
        for udata in demo_users_data:
            user, ucreated = User.objects.get_or_create(
                username=udata['username'],
                defaults={
                    'email': udata['email'],
                    'first_name': udata['first_name'],
                    'last_name': udata['last_name'],
                }
            )
            user.set_password('demo12345')
            user.first_name = udata['first_name']
            user.last_name = udata['last_name']
            user.email = udata['email']
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.location = udata['location']
            profile.phone = udata['phone']
            profile.bio = udata['bio']
            profile.save()

            users_dict[udata['username']] = user
            self.stdout.write(f"[OK] User '{user.username}' ready (password: demo12345)")

        # 3. Categories
        categories_data = [
            {'name': 'Electronics', 'icon': 'bi-laptop', 'description': 'Laptops, desktops, audio gear, TVs, and cutting-edge tech accessories.'},
            {'name': 'Vehicles', 'icon': 'bi-car-front', 'description': 'Bikes, scooters, cars, riding helmets, and genuine automotive gear.'},
            {'name': 'Mobiles', 'icon': 'bi-phone', 'description': 'Smartphones, tablets, smartwatches, and verified mobile accessories.'},
            {'name': 'Fashion', 'icon': 'bi-bag', 'description': 'Designer apparel, premium shoes, handcrafted bags, and stylish jewelry.'},
            {'name': 'Furniture', 'icon': 'bi-lamp', 'description': 'Ergonomic chairs, wooden desks, sofas, and cozy home furnishings.'},
            {'name': 'Books', 'icon': 'bi-book', 'description': 'Academic textbooks, competitive exam guides, novels, and rare collections.'},
            {'name': 'Home & Garden', 'icon': 'bi-flower1', 'description': 'Kitchen appliances, indoor plants, tools, and home improvement essentials.'},
            {'name': 'Sports', 'icon': 'bi-dribbble', 'description': 'Fitness weights, sports racquets, cycles, and workout gear.'},
            {'name': 'Other', 'icon': 'bi-grid', 'description': 'Musical instruments, art supplies, collectibles, and miscellaneous treasures.'},
        ]

        cat_dict = {}
        for cdata in categories_data:
            cat, c_created = Category.objects.get_or_create(
                name=cdata['name'],
                defaults={'icon': cdata['icon'], 'description': cdata['description']}
            )
            cat.icon = cdata['icon']
            cat.description = cdata['description']
            cat.save()
            cat_dict[cdata['name']] = cat
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(cat_dict)} Categories ready"))

        # 4. Products with real local media images
        media_products_dir = Path(settings.MEDIA_ROOT) / 'products'
        os.makedirs(media_products_dir, exist_ok=True)

        sample_products = [
            {
                'seller': 'rahul',
                'category': 'Mobiles',
                'title': 'Samsung Galaxy S23 5G (Phantom Black, 128GB)',
                'price': Decimal('44999.00'),
                'condition': 'LIKE_NEW',
                'location': 'Indiranagar, Bengaluru',
                'description': 'Selling my Samsung Galaxy S23 5G purchased 8 months ago. Flawless display with tempered glass installed on day one. Comes with original invoice, box, and fast charger cable. No scratches or dents. Battery health is at 98%. Selling because company provided a phone.',
                'filename': 'samsung_s23.jpg',
                'color': (15, 76, 129),
                'views': 84
            },
            {
                'seller': 'rahul',
                'category': 'Electronics',
                'title': 'HP Pavilion 15 Gaming Laptop (Ryzen 7, 16GB, RTX 3050)',
                'price': Decimal('54500.00'),
                'condition': 'GOOD',
                'location': 'Koramangala, Bengaluru',
                'description': 'High-performance HP Pavilion 15 laptop. AMD Ryzen 7 5800H processor with 16GB DDR4 RAM and 512GB NVMe SSD. Dedicated NVIDIA GeForce RTX 3050 4GB graphics. Clean keyboard, 144Hz IPS display. Ideal for coding, 3D modeling, and gaming. Original 200W charger included.',
                'filename': 'hp_pavilion.jpg',
                'color': (30, 41, 59),
                'views': 122
            },
            {
                'seller': 'rahul',
                'category': 'Electronics',
                'title': 'Sony WH-1000XM4 Wireless Noise Cancelling Headphones',
                'price': Decimal('16500.00'),
                'condition': 'LIKE_NEW',
                'location': 'Indiranagar, Bengaluru',
                'description': 'Legendary Sony WH-1000XM4 noise cancelling headphones in Midnight Silver. Industry-leading active noise cancellation with 30-hour battery life. Used only in office environment. Comes with hardshell travel case, 3.5mm cable, and flight adapter.',
                'filename': 'sony_headphones.jpg',
                'color': (45, 55, 72),
                'views': 65
            },
            {
                'seller': 'arjun',
                'category': 'Vehicles',
                'title': 'Royal Enfield Street Ace Matte Black Riding Helmet',
                'price': Decimal('2800.00'),
                'condition': 'GOOD',
                'location': 'Connaught Place, Delhi',
                'description': 'Genuine Royal Enfield ISI and DOT certified full face riding helmet. Size L (59-60cm). Scratch-resistant optical visor with UV protection. Inner liner freshly washed and sanitized. Never dropped or involved in accidents.',
                'filename': 're_helmet.jpg',
                'color': (24, 24, 27),
                'views': 47
            },
            {
                'seller': 'arjun',
                'category': 'Vehicles',
                'title': 'Decathlon Rockrider ST100 27.5T Mountain Bike',
                'price': Decimal('9200.00'),
                'condition': 'GOOD',
                'location': 'Saket, Delhi',
                'description': 'Lightweight aluminum frame mountain bicycle with 21-speed Shimano Tourney gears. 80mm front suspension fork. Recently serviced with brand new brake pads and lubricated chain. Free accessories: mudguards, bottle holder, and helmet.',
                'filename': 'rockrider_cycle.jpg',
                'color': (21, 94, 117),
                'views': 93
            },
            {
                'seller': 'priya',
                'category': 'Furniture',
                'title': 'Solid Sheesham Wood Study & Work Table with Drawers',
                'price': Decimal('7200.00'),
                'condition': 'LIKE_NEW',
                'location': 'Bandra West, Mumbai',
                'description': 'Handcrafted pure Sheesham wood study table with natural teak finish. Dimensions: 48 x 24 x 30 inches. Features 2 smooth gliding drawers and built-in cable pass-through hole. Extremely sturdy and stylish for modern home offices.',
                'filename': 'wooden_table.jpg',
                'color': (120, 53, 15),
                'views': 110
            },
            {
                'seller': 'priya',
                'category': 'Furniture',
                'title': 'Ergonomic High-Back Breathable Mesh Office Chair',
                'price': Decimal('5400.00'),
                'condition': 'GOOD',
                'location': 'Andheri East, Mumbai',
                'description': 'Ergonomic chair with 3D adjustable armrests, pneumatic height adjustment, and lumbar support tension control. Breathable Korean mesh back keeps you cool during long hours. Heavy duty nylon base with smooth caster wheels.',
                'filename': 'office_chair.jpg',
                'color': (51, 65, 85),
                'views': 78
            },
            {
                'seller': 'priya',
                'category': 'Furniture',
                'title': 'Contemporary 3-Seater Scandinavian Sofa (Slate Grey)',
                'price': Decimal('14500.00'),
                'condition': 'GOOD',
                'location': 'Bandra West, Mumbai',
                'description': 'Comfortable 3-seater sofa with high-density foam cushioning and premium stain-resistant fabric. Sturdy solid wood frame with tapered wooden legs. Purchased from Pepperfry 1.5 years ago. Selling due to interstate relocation.',
                'filename': 'grey_sofa.jpg',
                'color': (71, 85, 105),
                'views': 140
            },
            {
                'seller': 'sneha',
                'category': 'Fashion',
                'title': 'Nike Air Zoom Pegasus 39 Running Shoes (UK 9)',
                'price': Decimal('4200.00'),
                'condition': 'NEW',
                'location': 'Jubilee Hills, Hyderabad',
                'description': 'Brand new Nike Air Zoom Pegasus 39 in original box with tags attached. Colorway: Pure Platinum / Mineral Slate. UK Size 9 / US 10. Ordered wrong size online and missed return window. Unworn, 100% authentic.',
                'filename': 'nike_shoes.jpg',
                'color': (13, 148, 136),
                'views': 58
            },
            {
                'seller': 'sneha',
                'category': 'Fashion',
                'title': 'Handcrafted Full-Grain Leather Weekend Duffle Bag',
                'price': Decimal('3200.00'),
                'condition': 'LIKE_NEW',
                'location': 'Banjara Hills, Hyderabad',
                'description': 'Handcrafted vintage brown genuine leather duffle bag with brass hardware and reinforced YKK zippers. Detachable padded shoulder strap. Shoe compartment at base. Perfect for 3-day weekend trips or stylish gym sessions.',
                'filename': 'leather_bag.jpg',
                'color': (146, 64, 14),
                'views': 39
            },
            {
                'seller': 'rahul',
                'category': 'Books',
                'title': 'Computer Science & Algorithm Master Book Collection (8 Volumes)',
                'price': Decimal('1600.00'),
                'condition': 'LIKE_NEW',
                'location': 'Indiranagar, Bengaluru',
                'description': 'Complete set of engineering books including CLRS Introduction to Algorithms, Clean Code, Designing Data-Intensive Applications, and Python Cookbook. Crisp pages, no highlights or markings. Best bundle for coding interviews.',
                'filename': 'engineering_books.jpg',
                'color': (29, 78, 216),
                'views': 68
            },
            {
                'seller': 'arjun',
                'category': 'Books',
                'title': 'UPSC Civil Services Standard Reference Set (M. Laxmikanth + Spectrum)',
                'price': Decimal('1850.00'),
                'condition': 'GOOD',
                'location': 'Old Rajinder Nagar, Delhi',
                'description': 'Latest editions of Indian Polity by Laxmikanth, Modern History by Spectrum, and Certificate Physical Geography by Goh Cheng Leong. Great condition with careful annotations and summary slips included.',
                'filename': 'upsc_books.jpg',
                'color': (180, 83, 9),
                'views': 82
            },
            {
                'seller': 'priya',
                'category': 'Home & Garden',
                'title': 'Philips Digital Essential Air Fryer (4.1L RapidAir Tech)',
                'price': Decimal('4999.00'),
                'condition': 'LIKE_NEW',
                'location': 'Bandra West, Mumbai',
                'description': 'Philips 4.1L digital touchscreen air fryer with RapidAir technology for healthy cooking with up to 90% less oil. 7 preset cooking programs. Dishwasher safe removable basket. Clean and well maintained.',
                'filename': 'air_fryer.jpg',
                'color': (190, 24, 93),
                'views': 95
            },
            {
                'seller': 'arjun',
                'category': 'Sports',
                'title': 'Adjustable Rubber Coated Dumbbells Set 20KG with Connector',
                'price': Decimal('3200.00'),
                'condition': 'LIKE_NEW',
                'location': 'Connaught Place, Delhi',
                'description': 'Complete 20kg dumbbell and barbell set with non-slip foam bar connector. Floor-safe rubber coated weight plates with star lock collars. Ideal for full body home workouts without scratching flooring.',
                'filename': 'dumbbells_set.jpg',
                'color': (15, 23, 42),
                'views': 114
            },
            {
                'seller': 'rahul',
                'category': 'Electronics',
                'title': 'Logitech MX Master 3S Wireless Performance Mouse',
                'price': Decimal('6800.00'),
                'condition': 'LIKE_NEW',
                'location': 'Indiranagar, Bengaluru',
                'description': 'Flagship Logitech MX Master 3S mouse in Graphite. Ultra-quiet clicks, 8K DPI sensor that tracks on glass, and MagSpeed electromagnetic scroll wheel. Multi-device Bluetooth pairing for Mac and Windows. With original charging cable.',
                'filename': 'mx_master.jpg',
                'color': (30, 41, 59),
                'views': 76
            },
            {
                'seller': 'sneha',
                'category': 'Other',
                'title': 'Yamaha F280 Acoustic Guitar with Padded Gig Bag & Tuner',
                'price': Decimal('6500.00'),
                'condition': 'LIKE_NEW',
                'location': 'Jubilee Hills, Hyderabad',
                'description': 'Yamaha F280 dreadnought acoustic guitar in natural gloss finish. Warm resonant tone with low comfortable action. Fitted with DAddario strings. Includes heavy padded gig bag, digital clip-on tuner, and 3 guitar picks.',
                'filename': 'yamaha_guitar.jpg',
                'color': (161, 98, 7),
                'views': 89
            }
        ]

        created_products = []
        for pdata in sample_products:
            # Create local physical image file
            img_rel_path = f"products/{pdata['filename']}"
            img_abs_path = media_products_dir / pdata['filename']
            create_product_banner(
                file_path=str(img_abs_path),
                title=pdata['title'],
                category_name=pdata['category'],
                price_str=str(int(pdata['price'])),
                bg_color=pdata['color']
            )

            seller_user = users_dict[pdata['seller']]
            seller_phone = seller_user.profile.phone if hasattr(seller_user, 'profile') else '+91 98765 43210'

            product, p_created = Product.objects.get_or_create(
                title=pdata['title'],
                defaults={
                    'seller': seller_user,
                    'category': cat_dict[pdata['category']],
                    'price': pdata['price'],
                    'condition': pdata['condition'],
                    'location': pdata['location'],
                    'contact_phone': seller_phone,
                    'description': pdata['description'],
                    'image': img_rel_path,
                    'is_active': True,
                    'views': pdata['views']
                }
            )
            if not p_created:
                # Update attributes to ensure clean state
                product.seller = seller_user
                product.category = cat_dict[pdata['category']]
                product.price = pdata['price']
                product.condition = pdata['condition']
                product.location = pdata['location']
                product.contact_phone = seller_phone
                product.description = pdata['description']
                product.image = img_rel_path
                product.views = pdata['views']
                product.save()

            created_products.append(product)

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(created_products)} Realistic Product Listings seeded with valid images"))

        # 5. Sample Favorites
        fav_pairs = [
            ('priya', created_products[0]),  # Priya likes Samsung S23
            ('priya', created_products[4]),  # Priya likes Cycle
            ('rahul', created_products[5]),  # Rahul likes Wooden Table
            ('rahul', created_products[6]),  # Rahul likes Office Chair
            ('arjun', created_products[8]),  # Arjun likes Nike Shoes
            ('sneha', created_products[2]),  # Sneha likes Sony Headphones
            ('sneha', created_products[15]), # Sneha likes Yamaha Guitar
        ]
        for uname, prod in fav_pairs:
            Favorite.objects.get_or_create(user=users_dict[uname], product=prod)
        self.stdout.write(self.style.SUCCESS("[OK] Sample Favorites seeded"))

        # 6. Sample Contact Messages
        messages_data = [
            {
                'sender': 'priya',
                'receiver': 'rahul',
                'product': created_products[0],
                'phone': '+91 98200 98765',
                'message': 'Hi Rahul! Is the Samsung Galaxy S23 still available? Would you consider 42,000 for immediate cash pickup tomorrow?',
            },
            {
                'sender': 'rahul',
                'receiver': 'priya',
                'product': created_products[5],
                'phone': '+91 98451 23456',
                'message': 'Hello Priya, love the Sheesham study desk. Could you please confirm if the drawers have locks? I am located in Indiranagar and can arrange a Porter truck.',
            },
            ('sneha', 'arjun', created_products[4], '+91 98765 11223', 'Hi Arjun! Is the Rockrider cycle suitable for someone 5ft 8in tall? Can I come test ride this weekend?'),
        ]

        for item in messages_data:
            if isinstance(item, dict):
                ContactMessage.objects.get_or_create(
                    sender=users_dict[item['sender']],
                    receiver=users_dict[item['receiver']],
                    product=item['product'],
                    defaults={
                        'message': item['message'],
                        'sender_phone': item['phone'],
                        'is_read': False
                    }
                )
            else:
                s_name, r_name, p_obj, ph, txt = item
                ContactMessage.objects.get_or_create(
                    sender=users_dict[s_name],
                    receiver=users_dict[r_name],
                    product=p_obj,
                    defaults={'message': txt, 'sender_phone': ph, 'is_read': False}
                )
        self.stdout.write(self.style.SUCCESS("[OK] Sample Inquiries and Messages seeded"))

        self.stdout.write(self.style.SUCCESS("\n=========================================="))
        self.stdout.write(self.style.SUCCESS("MarketNest Database successfully seeded!"))
        self.stdout.write(self.style.SUCCESS("Admin Account: admin / admin123"))
        self.stdout.write(self.style.SUCCESS("Demo Users: rahul, priya, arjun, sneha (Password: demo12345)"))
        self.stdout.write(self.style.SUCCESS("==========================================\n"))
