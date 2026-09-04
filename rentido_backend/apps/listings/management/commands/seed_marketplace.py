from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import User, RoleChoices, UserRole, RenterProfile, OwnerProfile
from apps.categories.models import Category, CommissionRule
from apps.assets.models import Asset, VerificationStatus, AssetStatus
from apps.listings.models import Listing, PricingModel, ListingStatus
from apps.promotions.models import Coupon, DiscountType, SurgePricingRule
from apps.trust.models import TrustProfile, TrustTier, TrustEvent, TrustEventType
from apps.trust.services.scoring import TrustScoreEngine


class Command(BaseCommand):
    help = 'Seeds realistic, production-grade marketplace demo data into MySQL'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Rentido marketplace data..."))

        # 1. Categories
        categories_data = [
            ('Cameras & Optics', 'cameras-optics', 'Cinema cameras, DSLRs, anamorphic lenses, stabilizers'),
            ('Drones & Aerial Cinematography', 'drones-aerial', 'Commercial & cinematic 4K/8K camera drones'),
            ('Laptops & Workstations', 'laptops-workstations', 'Apple Silicon, NVIDIA RTX creative rendering workstations'),
            ('Studio Audio & DJ Sound', 'audio-studio', 'Microphones, audio interfaces, PA speakers, mixers'),
            ('Gaming & VR Consoles', 'gaming-vr', 'PS5, Xbox Series X, Meta Quest 3 VR headsets'),
            ('Electric Mobility & E-Bikes', 'electric-mobility', 'Electric bicycles, commuter scooters, city mobility'),
            ('Power Tools & Industrial', 'power-tools', 'Demolition drills, saws, pressure washers, generators'),
            ('Camping & Outdoor Expeditions', 'camping-outdoor', 'All-weather tents, trekking gear, portable power stations'),
        ]

        categories = {}
        for name, slug, desc in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc}
            )
            categories[slug] = cat

            # Dynamic commission rule: 10% with min ₹50, max ₹1500
            CommissionRule.objects.get_or_create(
                category=cat,
                defaults={
                    'commission_type': CommissionRule.CommissionType.PERCENTAGE,
                    'commission_value': Decimal('10.00'),
                    'minimum_fee': Decimal('50.00'),
                    'maximum_fee': Decimal('1500.00'),
                    'is_active': True
                }
            )

        self.stdout.write(self.style.SUCCESS(f"[OK] Created {len(categories)} categories and commission rules."))

        # 2. Key Users
        # Owner 1: Bangalore
        owner_blr, _ = User.objects.get_or_create(
            email='rajesh.camera@rentido.com',
            defaults={
                'username': 'rajesh_camera',
                'first_name': 'Rajesh',
                'last_name': 'Sharma',
                'phone_number': '+919876543210',
                'is_email_verified': True,
                'is_phone_verified': True,
            }
        )
        owner_blr.set_password('ownerpassword123')
        owner_blr.save()
        UserRole.objects.get_or_create(user=owner_blr, role=RoleChoices.OWNER)
        OwnerProfile.objects.get_or_create(user=owner_blr, defaults={'business_name': 'Apex Cinema Rentals', 'is_verified': True})
        
        # Owner 2: Mumbai
        owner_mum, _ = User.objects.get_or_create(
            email='priya.tech@rentido.com',
            defaults={
                'username': 'priya_tech',
                'first_name': 'Priya',
                'last_name': 'Mehta',
                'phone_number': '+919876543211',
                'is_email_verified': True,
                'is_phone_verified': True,
            }
        )
        owner_mum.set_password('ownerpassword123')
        owner_mum.save()
        UserRole.objects.get_or_create(user=owner_mum, role=RoleChoices.OWNER)
        OwnerProfile.objects.get_or_create(user=owner_mum, defaults={'business_name': 'TechVault Solutions', 'is_verified': True})

        # Renter: Bangalore
        renter_blr, _ = User.objects.get_or_create(
            email='ananya.renter@rentido.com',
            defaults={
                'username': 'ananya_renter',
                'first_name': 'Ananya',
                'last_name': 'Verma',
                'phone_number': '+919876543212',
                'is_email_verified': True,
                'is_phone_verified': True,
            }
        )
        renter_blr.set_password('renterpassword123')
        renter_blr.save()
        UserRole.objects.get_or_create(user=renter_blr, role=RoleChoices.RENTER)
        RenterProfile.objects.get_or_create(
            user=renter_blr,
            defaults={
                'city': 'Bangalore',
                'emergency_contact': '+919876543299',
                'address': '104, 12th Main, Indiranagar',
                'kyc_verified': True,
            }
        )

        # Driver
        driver_blr, _ = User.objects.get_or_create(
            email='arun.driver@rentido.com',
            defaults={
                'username': 'arun_driver',
                'first_name': 'Arun',
                'last_name': 'Kumar',
                'phone_number': '+919876543213',
                'is_email_verified': True,
                'is_phone_verified': True,
            }
        )
        driver_blr.set_password('driverpassword123')
        driver_blr.save()
        UserRole.objects.get_or_create(user=driver_blr, role=RoleChoices.DRIVER)

        # Trust Profiles
        p1, _ = TrustProfile.objects.get_or_create(user=owner_blr)
        p1.trust_score = 620
        p1.tier = TrustTier.GOLD
        p1.completed_rentals_count = 38
        p1.save()

        p2, _ = TrustProfile.objects.get_or_create(user=owner_mum)
        p2.trust_score = 740
        p2.tier = TrustTier.PLATINUM
        p2.completed_rentals_count = 85
        p2.save()

        p3, _ = TrustProfile.objects.get_or_create(user=renter_blr)
        p3.trust_score = 240
        p3.tier = TrustTier.SILVER
        p3.completed_rentals_count = 6
        p3.save()

        self.stdout.write(self.style.SUCCESS("[OK] Seeded verified Owner, Renter, Driver, and Trust Profiles."))

        # 3. Physical Assets & Commercial Listings
        gear_catalog = [
            {
                'owner': owner_blr,
                'category': categories['cameras-optics'],
                'name': 'Sony FX3 Full-Frame Cinema Camera',
                'brand': 'Sony',
                'model': 'ILME-FX3',
                'serial': 'SN-SONY-FX3-7712',
                'replacement': Decimal('320000.00'),
                'title': 'Sony FX3 Full-Frame Cinema Camera (4K 120p / 10-Bit 4:2:2)',
                'desc': 'Includes XLR top handle, 3x batteries, 160GB CFexpress Type A card, cage, and charger. Ideal for indie films, commercial shoots, and music videos.',
                'price': Decimal('2800.00'),
                'deposit': Decimal('15000.00'),
                'city': 'Bangalore',
                'area': 'Indiranagar',
                'pincode': '560038',
                'delivery': True,
            },
            {
                'owner': owner_blr,
                'category': categories['cameras-optics'],
                'name': 'Canon EOS R5 Mirrorless Camera Body',
                'brand': 'Canon',
                'model': 'EOS R5',
                'serial': 'SN-CANON-R5-9944',
                'replacement': Decimal('280000.00'),
                'title': 'Canon EOS R5 8K Full-Frame Mirrorless Kit',
                'desc': '45MP full-frame CMOS sensor, 8K30 Raw recording, in-body 5-axis stabilization. Includes 2x LP-E6NH batteries, fast dual-slot charger, 512GB CFexpress card.',
                'price': Decimal('2500.00'),
                'deposit': Decimal('12000.00'),
                'city': 'Bangalore',
                'area': 'Koramangala',
                'pincode': '560034',
                'delivery': True,
            },
            {
                'owner': owner_mum,
                'category': categories['laptops-workstations'],
                'name': 'Apple MacBook Pro 16-inch M3 Max',
                'brand': 'Apple',
                'model': 'MacBook Pro 16" M3 Max',
                'serial': 'SN-MBP16-M3-8821',
                'replacement': Decimal('380000.00'),
                'title': 'Apple MacBook Pro 16" (M3 Max, 64GB Unified RAM, 1TB SSD)',
                'desc': '16-core CPU, 40-core GPU, Liquid Retina XDR display. Pre-installed with DaVinci Resolve Studio and Adobe Creative Cloud for on-set DIT and 8K rendering.',
                'price': Decimal('2200.00'),
                'deposit': Decimal('20000.00'),
                'city': 'Mumbai',
                'area': 'Bandra West',
                'pincode': '400050',
                'delivery': True,
            },
            {
                'owner': owner_blr,
                'category': categories['drones-aerial'],
                'name': 'DJI Mavic 3 Pro Cine Combo Drone',
                'brand': 'DJI',
                'model': 'Mavic 3 Pro Cine',
                'serial': 'SN-DJI-M3P-4401',
                'replacement': Decimal('350000.00'),
                'title': 'DJI Mavic 3 Pro Cine Combo (Hasselblad Tri-Camera Apple ProRes)',
                'desc': 'Apple ProRes 422 HQ, built-in 1TB SSD, 3x batteries (up to 2 hours flight time), DJI RC Pro smart remote, ND filter set, and rugged flight case.',
                'price': Decimal('3200.00'),
                'deposit': Decimal('18000.00'),
                'city': 'Bangalore',
                'area': 'Whitefield',
                'pincode': '560066',
                'delivery': True,
            },
            {
                'owner': owner_mum,
                'category': categories['audio-studio'],
                'name': 'Shure SM7B Vocal Dynamic Studio Mic',
                'brand': 'Shure',
                'model': 'SM7B',
                'serial': 'SN-SHURE-SM7B-5532',
                'replacement': Decimal('45000.00'),
                'title': 'Shure SM7B Vocal Dynamic Mic + Cloudlifter CL-1',
                'desc': 'The broadcast and podcast gold standard. Includes Cloudlifter CL-1 inline preamp for ultra-clean 25dB gain, Rode PSA1 boom arm, and 3m Mogami XLR cable.',
                'price': Decimal('850.00'),
                'deposit': Decimal('5000.00'),
                'city': 'Mumbai',
                'area': 'Andheri West',
                'pincode': '400053',
                'delivery': False,
            },
            {
                'owner': owner_blr,
                'category': categories['gaming-vr'],
                'name': 'Sony PlayStation 5 Console + PS VR2 Headset',
                'brand': 'Sony',
                'model': 'PS5 Disc Edition + VR2',
                'serial': 'SN-PS5-VR2-1199',
                'replacement': Decimal('115000.00'),
                'title': 'Sony PlayStation 5 + PS VR2 4K HDR Virtual Reality Bundle',
                'desc': 'Complete party and gaming bundle: 2x DualSense wireless controllers, Horizon Call of the Mountain, Gran Turismo 7, FIFA 24, charging dock, and travel bag.',
                'price': Decimal('1400.00'),
                'deposit': Decimal('8000.00'),
                'city': 'Bangalore',
                'area': 'HSR Layout',
                'pincode': '560102',
                'delivery': True,
            },
            {
                'owner': owner_mum,
                'category': categories['electric-mobility'],
                'name': 'EMotorad E-Bike 250W All-Terrain',
                'brand': 'EMotorad',
                'model': 'T-Rex Pro',
                'serial': 'SN-EMOTORAD-TREX-7744',
                'replacement': Decimal('55000.00'),
                'title': 'EMotorad T-Rex Pro Electric Mountain Bike (50km Range)',
                'desc': 'Removable 36V 10.4Ah Li-ion battery, front suspension fork, dual disc brakes, 7-speed Shimano gears, helmet and safety lock included.',
                'price': Decimal('600.00'),
                'deposit': Decimal('4000.00'),
                'city': 'Mumbai',
                'area': 'Juhu',
                'pincode': '400049',
                'delivery': False,
            },
            {
                'owner': owner_blr,
                'category': categories['power-tools'],
                'name': 'Bosch Professional SDS-Plus Rotary Hammer Drill',
                'brand': 'Bosch',
                'model': 'GBH 2-28 F',
                'serial': 'SN-BOSCH-GBH-9922',
                'replacement': Decimal('22000.00'),
                'title': 'Bosch GBH 2-28 F Professional Rotary Hammer Drill Kit',
                'desc': '880W heavy-duty hammer drill with kickback control, interchangeable quick-change chuck, set of 5 concrete drill bits, and heavy-duty case.',
                'price': Decimal('550.00'),
                'deposit': Decimal('3000.00'),
                'city': 'Bangalore',
                'area': 'Electronic City',
                'pincode': '560100',
                'delivery': True,
            },
        ]

        created_listings_count = 0
        for item in gear_catalog:
            asset, _ = Asset.objects.get_or_create(
                serial_number=item['serial'],
                defaults={
                    'owner': item['owner'],
                    'category': item['category'],
                    'name': item['name'],
                    'brand': item['brand'],
                    'model_name': item['model'],
                    'replacement_value': item['replacement'],
                    'verification_status': VerificationStatus.VERIFIED,
                    'status': AssetStatus.AVAILABLE,
                }
            )

            listing, created = Listing.objects.get_or_create(
                asset=asset,
                defaults={
                    'title': item['title'],
                    'description': item['desc'],
                    'rental_price': item['price'],
                    'pricing_model': PricingModel.DAILY,
                    'security_deposit': item['deposit'],
                    'city': item['city'],
                    'area': item['area'],
                    'pincode': item['pincode'],
                    'is_delivery_available': item['delivery'],
                    'is_self_pickup_available': True,
                    'status': ListingStatus.PUBLISHED,
                }
            )
            if created:
                created_listings_count += 1

        self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(gear_catalog)} physical assets and commercial listings."))

        # 4. Promotional Coupons
        coupons = [
            ('WELCOME20', '20% Welcome Offer', DiscountType.PERCENTAGE, Decimal('20.00'), Decimal('1000.00'), Decimal('500.00')),
            ('FREEDELIVERY', 'Free Doorstep Delivery', DiscountType.FLAT, Decimal('150.00'), None, Decimal('500.00')),
            ('FESTIVE500', 'Rs. 500 Off Festival Special', DiscountType.FLAT, Decimal('500.00'), None, Decimal('2500.00')),
        ]

        for code, title, dtype, val, cap, min_rent in coupons:
            Coupon.objects.get_or_create(
                code=code,
                defaults={
                    'title': title,
                    'discount_type': dtype,
                    'discount_value': val,
                    'max_discount_amount': cap,
                    'minimum_rental_amount': min_rent,
                    'is_active': True,
                }
            )

        self.stdout.write(self.style.SUCCESS(f"[OK] Seeded promotional coupons (WELCOME20, FREEDELIVERY, FESTIVE500)."))

        # 5. Dynamic Surge Rule
        now = timezone.now()
        SurgePricingRule.objects.get_or_create(
            name='Diwali Weekend Cinema Rush',
            defaults={
                'city': 'Bangalore',
                'category': categories['cameras-optics'],
                'multiplier': Decimal('1.15'),
                'start_datetime': now - timedelta(days=2),
                'end_datetime': now + timedelta(days=14),
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS(f"[OK] Seeded dynamic surge pricing rule."))

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] MARKETPLACE DATA SEEDED SUCCESSFULLY!"))
