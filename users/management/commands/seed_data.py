# core/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
import random # For randomizing users and comments

from users.models import CustomUser
from users.models import GoalCategory, SubCategory, Goal, GoalStreak, GoalMessage # Import GoalMessage

class Command(BaseCommand):
    help = 'Populates the database with initial GoalCategory, SubCategory, Goal, GoalStreak, and GoalMessage data.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Ma\'lumotlarni yuklash boshlandi...'))

        # Ma'lumotlarni tozalash (chet el kalitlari tufayli tartib muhim)
        self.stdout.write(self.style.WARNING('Mavjud ma\'lumotlar tozalanmoqda...'))
        GoalMessage.objects.all().delete() # Yangi: Xabarlarni birinchi o'chirish
        GoalStreak.objects.all().delete()
        Goal.objects.all().delete()
        SubCategory.objects.all().delete()
        GoalCategory.objects.all().delete()
        # Namuna foydalanuvchilarni o'chirish (faqat biz yaratganlarni)
        CustomUser.objects.filter(username__in=[
            'ali_valiyev', 'gulnora_axmedova', 'javohir_karimov', 'nodira_saidova',
            'sardor_umarov', 'dilnoza_rustamova', 'aziz_odilov', 'mariya_ismoilova',
            'bekzod_fayziev', 'shaxnoza_azimova', 'farhod_ergashev', 'zuhra_karimova',
            'sampleuser' # Zaxira foydalanuvchi
        ]).delete()
        self.stdout.write(self.style.WARNING('Mavjud ma\'lumotlar muvaffaqiyatli tozalandi.'))

        # --- Maqsad Kategoriyalarini Yaratish ---
        self.stdout.write(self.style.SUCCESS('Maqsad Kategoriyasi ma\'lumotlari yuklanmoqda...'))
        categories_data = [
            {'name': "Sport", 'color': "#E2FDF2", 'icon': "hi-bolt"},
            {'name': "Ta’lim", 'color': "#F4F4F4", 'icon': "hi-academic-cap"},
            {'name': "Zamonaviy kasblar", 'color': "#F1E3FF", 'icon': "hi-code"},
            {'name': "Shaxsiy rivojlanish", 'color': "#D1F1FF", 'icon': "hi-sparkles"},
            {'name': "Kitobxonlik", 'color': "#FFE680", 'icon': "hi-book-open"},
            {'name': "Biznes", 'color': "#AFFF6C", 'icon': "hi-briefcase"},
            {'name': 'Sayahat', 'color': '#FF6B6B', 'icon': 'hi-globe-alt'},
            {'name': 'Qiziqishlar', 'color': '#6BEBFF', 'icon': 'hi-heart'},
            {'name': 'Karyera', 'color': '#D1FF6B', 'icon': 'hi-briefcase'},
            {'name': 'Til o\'rganish', 'color': '#CCCCCC', 'icon': 'hi-language'},
            {'name': 'Volontyorlik', 'color': '#FFC0CB', 'icon': 'hi-hand-raised'},
            {'name': 'Ustoz-Shogirt', 'color': '#B0FFB0', 'icon': 'hi-users'},
        ]

        created_categories = {}
        for data in categories_data:
            category, created = GoalCategory.objects.get_or_create(
                name=data['name'],
                defaults={'color': data['color'], 'icon': data['icon'], 'slug': slugify(data['name'])}
            )
            created_categories[data['name']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f"Kategoriya yaratildi: {data['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Kategoriya allaqachon mavjud: {data['name']}"))

        self.stdout.write(self.style.SUCCESS('Maqsad Kategoriyasi ma\'lumotlari yuklandi!'))

        # --- Ichki Yo'nalishlarni Yaratish ---
        self.stdout.write(self.style.SUCCESS('Ichki Yo\'nalish ma\'lumotlari yuklanmoqda...'))
        subcategories_data = [
            {'category_name': 'Sport', 'name': 'Yugurish'}, {'category_name': 'Sport', 'name': 'Suzish'},
            {'category_name': 'Sport', 'name': 'Velosiped'}, {'category_name': 'Sport', 'name': 'Yoga'},
            {'category_name': 'Ta’lim', 'name': 'Dasturlash'}, {'category_name': 'Ta’lim', 'name': 'Marketing'},
            {'category_name': 'Ta’lim', 'name': 'Ma\'lumotlar tahlili'}, {'category_name': 'Ta’lim', 'name': 'Grafik dizayn'},
            {'category_name': 'Kitobxonlik', 'name': 'Fantastika'}, {'category_name': 'Kitobxonlik', 'name': 'Ilmiy'},
            {'category_name': 'Kitobxonlik', 'name': 'Tarixiy roman'}, {'category_name': 'Kitobxonlik', 'name': 'Biznes adabiyoti'},
            {'category_name': 'Biznes', 'name': 'Startap'}, {'category_name': 'Biznes', 'name': 'Investitsiya'},
            {'category_name': 'Biznes', 'name': 'Frilans'}, {'category_name': 'Biznes', 'name': 'Elektron tijorat'},
            {'category_name': 'Shaxsiy rivojlanish', 'name': 'Vaqtni boshqarish'}, {'category_name': 'Shaxsiy rivojlanish', 'name': 'Stressni yengish'},
            {'category_name': 'Shaxsiy rivojlanish', 'name': 'O\'z-o\'zini anglash'}, {'category_name': 'Shaxsiy rivojlanish', 'name': 'Muloqot ko\'nikmalari'},
            {'category_name': 'Sayahat', 'name': 'Yangi shaharni kashf qilish'}, {'category_name': 'Sayahat', 'name': 'Tabiat qo\'ynida dam olish'},
            {'category_name': 'Qiziqishlar', 'name': 'Fotosurat'}, {'category_name': 'Qiziqishlar', 'name': 'Pazandachilik'},
            {'category_name': 'Qiziqishlar', 'name': 'Musiqa chalish'},
            {'category_name': 'Karyera', 'name': 'Ish qidirish'}, {'category_name': 'Karyera', 'name': 'Professional sertifikat'},
            {'category_name': 'Til o\'rganish', 'name': 'Ingliz tili'}, {'category_name': 'Til o\'rganish', 'name': 'Nemis tili'},
            {'category_name': 'Til o\'rganish', 'name': 'Koreys tili'},
            {'category_name': 'Volontyorlik', 'name': 'Atrof-muhitni tozalash'}, {'category_name': 'Volontyorlik', 'name': 'Keksalarga yordam'},
            {'category_name': 'Ustoz-Shogirt', 'name': 'Mentor topish'}, {'category_name': 'Ustoz-Shogirt', 'name': 'Shogirt tayyorlash'},
        ]

        for data in subcategories_data:
            category = created_categories.get(data['category_name'])
            if category:
                SubCategory.objects.get_or_create(category=category, name=data['name'])
                self.stdout.write(self.style.SUCCESS(f"Ichki yo'nalish yaratildi: {data['name']} ({data['category_name']} ostida)"))
            else:
                self.stdout.write(self.style.ERROR(f"'{data['category_name']}' kategoriyasi topilmadi, ichki yo'nalish '{data['name']}' uchun."))
        self.stdout.write(self.style.SUCCESS('Ichki Yo\'nalish ma\'lumotlari yuklandi!'))

        # --- O'zbek Namuna Foydalanuvchilarni Yaratish (10+ foydalanuvchi) ---
        self.stdout.write(self.style.SUCCESS('CustomUser ma\'lumotlari yuklanmoqda...'))
        users_data = [
            {'username': 'ali_valiyev', 'first_name': 'Ali', 'last_name': 'Valiyev', 'email': 'ali@example.com', 'password': 'password123'},
            {'username': 'gulnora_axmedova', 'first_name': 'Gulnora', 'last_name': 'Axmedova', 'email': 'gulnora@example.com', 'password': 'password123'},
            {'username': 'javohir_karimov', 'first_name': 'Javohir', 'last_name': 'Karimov', 'email': 'javohir@example.com', 'password': 'password123'},
            {'username': 'nodira_saidova', 'first_name': 'Nodira', 'last_name': 'Saidova', 'email': 'nodira@example.com', 'password': 'password123'},
            {'username': 'sardor_umarov', 'first_name': 'Sardor', 'last_name': 'Umarov', 'email': 'sardor@example.com', 'password': 'password123'},
            {'username': 'dilnoza_rustamova', 'first_name': 'Dilnoza', 'last_name': 'Rustamova', 'email': 'dilnoza@example.com', 'password': 'password123'},
            {'username': 'aziz_odilov', 'first_name': 'Aziz', 'last_name': 'Odilov', 'email': 'aziz@example.com', 'password': 'password123'},
            {'username': 'mariya_ismoilova', 'first_name': 'Mariya', 'last_name': 'Ismoilova', 'email': 'mariya@example.com', 'password': 'password123'},
            {'username': 'bekzod_fayziev', 'first_name': 'Bekzod', 'last_name': 'Fayziev', 'email': 'bekzod@example.com', 'password': 'password123'},
            {'username': 'shaxnoza_azimova', 'first_name': 'Shaxnoza', 'last_name': 'Azimova', 'email': 'shaxnoza@example.com', 'password': 'password123'},
            {'username': 'farhod_ergashev', 'first_name': 'Farhod', 'last_name': 'Ergashev', 'email': 'farhod@example.com', 'password': 'password123'},
            {'username': 'zuhra_karimova', 'first_name': 'Zuhra', 'last_name': 'Karimova', 'email': 'zuhra@example.com', 'password': 'password123'},
        ]

        created_users = []
        for user_data in users_data:
            user, created = CustomUser.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email'],
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Foydalanuvchi yaratildi: {user.username}"))
            else:
                self.stdout.write(self.style.WARNING(f"Foydalanuvchi allaqachon mavjud: {user.username}"))
            created_users.append(user)

        if not created_users: # Zaxira foydalanuvchi, agar yuqorida hech kim yaratilmagan bo'lsa
            self.stdout.write(self.style.WARNING('Yuklashdan keyin foydalanuvchilar topilmadi. Zaxira namuna foydalanuvchi yaratilmoqda.'))
            user = CustomUser.objects.create_user(username='sampleuser', email='fallback@example.com', password='password123')
            created_users.append(user)
            self.stdout.write(self.style.SUCCESS(f"Zaxira namuna foydalanuvchi yaratildi: {user.username}"))

        self.stdout.write(self.style.SUCCESS('CustomUser ma\'lumotlari yuklandi!'))

        # --- Namuna Maqsadlarni Yaratish ---
        self.stdout.write(self.style.SUCCESS('Maqsad ma\'lumotlari yuklanmoqda...'))
        num_users = len(created_users)
        user_index = 0

        goals_data = [
            # Sport Maqsadlari (4)
            {'title': 'Har kuni 5 km yugurish', 'description': 'Jismoniy holatni yaxshilash va chidamlilikni oshirish.', 'category_name': 'Sport', 'sub_category_name': 'Yugurish', 'duration': 28, 'visibility': 'public'},
            {'title': 'Haftasiga 3 marta suzish', 'description': 'Yurak-qon tomir tizimini mustahkamlash.', 'category_name': 'Sport', 'sub_category_name': 'Suzish', 'duration': 21, 'visibility': 'public'},
            {'title': 'Har kuni 30 daqiqa yoga bilan shug\'ullanish', 'description': 'Moslashuvchanlikni oshirish va stressni kamaytirish.', 'category_name': 'Sport', 'sub_category_name': 'Yoga', 'duration': 14, 'visibility': 'private'},
            {'title': '100 km velosipedda yurish', 'description': 'Velosipedda uzoq masofalarga sayohat qilishga tayyorgarlik.', 'category_name': 'Sport', 'sub_category_name': 'Velosiped', 'duration': 28, 'visibility': 'public'},

            # Ta'lim Maqsadlari (4)
            {'title': 'Python dasturlash asoslarini o\'rganish', 'description': 'Dasturlash bo\'yicha bilimimni oshirish.', 'category_name': 'Ta’lim', 'sub_category_name': 'Dasturlash', 'duration': 21, 'visibility': 'public'},
            {'title': 'Raqamli marketing kursini tugatish', 'description': 'Onlayn marketing ko\'nikmalarini rivojlantirish.', 'category_name': 'Ta’lim', 'sub_category_name': 'Marketing', 'duration': 28, 'visibility': 'public'},
            {'title': 'Ma\'lumotlar tahlili bo\'yicha sertifikat olish', 'description': 'Katta ma\'lumotlar bilan ishlashni o\'rganish.', 'category_name': 'Ta’lim', 'sub_category_name': 'Ma\'lumotlar tahlili', 'duration': 28, 'visibility': 'private'},
            {'title': 'Grafik dizayn asoslarini o\'zlashtirish', 'description': 'Vizual kontent yaratish ko\'nikmalarini rivojlantirish.', 'category_name': 'Ta’lim', 'sub_category_name': 'Grafik dizayn', 'duration': 21, 'visibility': 'public'},

            # Kitobxonlik Maqsadlari (4)
            {'title': 'Haftasiga 2 ta kitob o\'qish', 'description': 'O\'qish ko\'nikmalarini rivojlantirish va yangi g\'oyalarni o\'rganish.', 'category_name': 'Kitobxonlik', 'sub_category_name': 'Fantastika', 'duration': 14, 'visibility': 'public'},
            {'title': 'Bir oyda bir ilmiy kitobni tugatish', 'description': 'Ilmiy bilimlarni kengaytirish.', 'category_name': 'Kitobxonlik', 'sub_category_name': 'Ilmiy', 'duration': 28, 'visibility': 'public'},
            {'title': 'O\'zbekiston tarixi bo\'yicha roman o\'qish', 'description': 'Vatan tarixi haqida chuqurroq ma\'lumot olish.', 'category_name': 'Kitobxonlik', 'sub_category_name': 'Tarixiy roman', 'duration': 21, 'visibility': 'private'},
            {'title': 'Biznes adabiyoti bo\'yicha 3 ta kitob o\'qish', 'description': 'Tadbirkorlik ko\'nikmalarini oshirish.', 'category_name': 'Kitobxonlik', 'sub_category_name': 'Biznes adabiyoti', 'duration': 28, 'visibility': 'public'},

            # Biznes Maqsadlari (4)
            {'title': 'Yangi startap g\'oyasini ishlab chiqish', 'description': 'Biznes rejasini tuzish va bozor tahlilini o\'tkazish.', 'category_name': 'Biznes', 'sub_category_name': 'Startap', 'duration': 28, 'visibility': 'public'},
            {'title': 'Kichik investitsiya portfelini yaratish', 'description': 'Moliyaviy savodxonlikni oshirish va daromad manbalarini diversifikatsiya qilish.', 'category_name': 'Biznes', 'sub_category_name': 'Investitsiya', 'duration': 21, 'visibility': 'private'},
            {'title': 'Frilans platformasida birinchi buyurtmani olish', 'description': 'O\'z xizmatlarimni onlayn taklif qilishni boshlash.', 'category_name': 'Biznes', 'sub_category_name': 'Frilans', 'duration': 14, 'visibility': 'public'},
            {'title': 'Elektron tijorat do\'konini ishga tushirish', 'description': 'Onlayn mahsulot sotish uchun platforma yaratish.', 'category_name': 'Biznes', 'sub_category_name': 'Elektron tijorat', 'duration': 28, 'visibility': 'public'},

            # Shaxsiy rivojlanish Maqsadlari (4)
            {'title': 'Stressni boshqarish texnikalarini o\'zlashtirish', 'description': 'Kundalik stressni kamaytirish va ruhiy salomatlikni yaxshilash.', 'category_name': 'Shaxsiy rivojlanish', 'sub_category_name': 'Stressni yengish', 'duration': 7, 'visibility': 'private'},
            {'title': 'Har kuni 15 daqiqa meditatsiya qilish', 'description': 'Diqqatni jamlash va ichki tinchlikni topish.', 'category_name': 'Shaxsiy rivojlanish', 'sub_category_name': 'O\'z-o\'zini anglash', 'duration': 21, 'visibility': 'public'},
            {'title': 'Vaqtni samarali boshqarish ko\'nikmalarini rivojlantirish', 'description': 'Kunlik vazifalarni rejalashtirish va unumdorlikni oshirish.', 'category_name': 'Shaxsiy rivojlanish', 'sub_category_name': 'Vaqtni boshqarish', 'duration': 14, 'visibility': 'public'},
            {'title': 'Jamoat oldida nutq so\'zlashdan qo\'rqmaslik', 'description': 'Muloqot ko\'nikmalarini yaxshilash va o\'ziga ishonchni oshirish.', 'category_name': 'Shaxsiy rivojlanish', 'sub_category_name': 'Muloqot ko\'nikmalari', 'duration': 28, 'visibility': 'public'},

            # Sayahat Maqsadlari (2)
            {'title': 'Yangi mamlakatga sayohat qilishni rejalashtirish', 'description': 'Madaniyatlarni o\'rganish va yangi joylarni kashf etish.', 'category_name': 'Sayahat', 'sub_category_name': 'Yangi shaharni kashf qilish', 'duration': 28, 'visibility': 'public'},
            {'title': 'Tog\'larga chiqish safarini uyushtirish', 'description': 'Tabiat qo\'ynida dam olish va faol hordiq chiqarish.', 'category_name': 'Sayahat', 'sub_category_name': 'Tabiat qo\'ynida dam olish', 'duration': 14, 'visibility': 'private'},

            # Qiziqishlar Maqsadlari (3)
            {'title': 'Professional fotosurat kursini tugatish', 'description': 'Fotosurat olish mahoratimni oshirish.', 'category_name': 'Qiziqishlar', 'sub_category_name': 'Fotosurat', 'duration': 21, 'visibility': 'public'},
            {'title': '5 ta yangi taom pishirishni o\'rganish', 'description': 'Pazandachilik ko\'nikmalarimni kengaytirish.', 'category_name': 'Qiziqishlar', 'sub_category_name': 'Pazandachilik', 'duration': 14, 'visibility': 'public'},
            {'title': 'Gitara chalishni boshlash', 'description': 'Yangi musiqa asbobini o\'zlashtirish.', 'category_name': 'Qiziqishlar', 'sub_category_name': 'Musiqa chalish', 'duration': 28, 'visibility': 'private'},

            # Karyera Maqsadlari (2)
            {'title': 'Yangi ish topish', 'description': 'Karyerada o\'sish va yangi imkoniyatlarni izlash.', 'category_name': 'Karyera', 'sub_category_name': 'Ish qidirish', 'duration': 28, 'visibility': 'public'},
            {'title': 'Professional sertifikat olish', 'description': 'O\'z sohamda bilimimni rasman tasdiqlash.', 'category_name': 'Karyera', 'sub_category_name': 'Professional sertifikat', 'duration': 21, 'visibility': 'public'},

            # Til o'rganish Maqsadlari (3)
            {'title': 'Ingliz tilida erkin gapirishni o\'rganish', 'description': 'Nutq va tushunish qobiliyatini yaxshilash.', 'category_name': 'Til o\'rganish', 'sub_category_name': 'Ingliz tili', 'duration': 28, 'visibility': 'public'},
            {'title': 'Nemis tili asoslarini o\'zlashtirish', 'description': 'Yangi til o\'rganishga kirish.', 'category_name': 'Til o\'rganish', 'sub_category_name': 'Nemis tili', 'duration': 21, 'visibility': 'private'},
            {'title': 'Koreys tilida oddiy suhbat qurish', 'description': 'Koreys madaniyatiga qiziqish tufayli til o\'rganish.', 'category_name': 'Til o\'rganish', 'sub_category_name': 'Koreys tili', 'duration': 28, 'visibility': 'public'},

            # Volontyorlik Maqsadlari (2)
            {'title': 'Mahalliy bog\'ni tozalashda ishtirok etish', 'description': 'Jamiyatga foyda keltirish va atrof-muhitni yaxshilash.', 'category_name': 'Volontyorlik', 'sub_category_name': 'Atrof-muhitni tozalash', 'duration': 7, 'visibility': 'public'},
            {'title': 'Keksa yoshdagi qo\'shniga yordam berish', 'description': 'Ijtimoiy mas\'uliyatni bajarish.', 'category_name': 'Volontyorlik', 'sub_category_name': 'Keksalarga yordam', 'duration': 14, 'visibility': 'private'},

            # Ustoz-Shogirt Maqsadlari (2)
            {'title': 'O\'z sohamda mentor topish', 'description': 'Tajribali mutaxassisdan bilim olish.', 'category_name': 'Ustoz-Shogirt', 'sub_category_name': 'Mentor topish', 'duration': 21, 'visibility': 'public'},
            {'title': 'Yosh mutaxassisga ustozlik qilish', 'description': 'O\'z bilimlarimni bo\'lishish va boshqalarga yordam berish.', 'category_name': 'Ustoz-Shogirt', 'sub_category_name': 'Shogirt tayyorlash', 'duration': 28, 'visibility': 'public'},
        ]

        created_goals = []
        for data in goals_data:
            category = created_categories.get(data['category_name'])
            sub_category = None
            if data.get('sub_category_name'):
                sub_category = SubCategory.objects.filter(category=category, name=data['sub_category_name']).first()

            if category:
                current_user = created_users[user_index % num_users]
                user_index += 1

                goal, created = Goal.objects.get_or_create(
                    title=data['title'],
                    defaults={
                        'description': data['description'],
                        'category': category,
                        'sub_category': sub_category,
                        'duration': data['duration'],
                        'visibility': data['visibility'],
                        'created_by': current_user,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Maqsad yaratildi: '{data['title']}' ({current_user.username} uchun)"))
                    created_goals.append(goal)
                else:
                    self.stdout.write(self.style.WARNING(f"Maqsad allaqachon mavjud: '{data['title']}'"))
            else:
                self.stdout.write(self.style.ERROR(f"'{data['category_name']}' kategoriyasi topilmadi, maqsad '{data['title']}' uchun."))

        self.stdout.write(self.style.SUCCESS('Maqsad ma\'lumotlari yuklandi!'))

        # --- Maqsad Streyklarini Yaratish (Faqat 1 kunlik streyklar) ---
        self.stdout.write(self.style.SUCCESS('Maqsad Streak ma\'lumotlari yuklanmoqda (faqat 1 kunlik)...'))
        today = timezone.now().date()
        
        # Har bir yaratilgan maqsad uchun, uni yaratgan foydalanuvchiga 1 kunlik streyk berish
        for goal in created_goals:
            GoalStreak.objects.get_or_create(
                user=goal.created_by,
                goal=goal,
                date=today,
                defaults={'streak_count': 1}
            )
            self.stdout.write(self.style.SUCCESS(f"'{goal.created_by.username}' uchun '{goal.title}' maqsadiga 1 kunlik streyk qo'shildi."))

        self.stdout.write(self.style.SUCCESS('Maqsad Streak ma\'lumotlari yuklandi!'))

        # --- Maqsad Izohlarini Yaratish (30+ izoh) ---
        self.stdout.write(self.style.SUCCESS('Maqsad Izoh (GoalMessage) ma\'lumotlari yuklanmoqda...'))
        
        sample_comments = [
            "Ajoyib maqsad! Sizga omad tilayman!",
            "Bu juda qiziqarli g'oya, men ham shunga o'xshash maqsad qo'ymoqchiman.",
            "Qanday qilib boshladingiz? Maslahatlaringiz bormi?",
            "Davom eting! Maqsadga erishishingizga ishonaman.",
            "Bu maqsadga erishish uchun qanday resurslardan foydalanyapsiz?",
            "Zo'r! Natijalarni kutib qolaman.",
            "Sizning intilishingiz meni ilhomlantirdi.",
            "Qiyinchiliklar bo'ladimi? Ularni qanday yengyapsiz?",
            "Bu maqsad uchun eng muhim qadam nima deb o'ylaysiz?",
            "Men ham bu yo'nalishda ishlayapman, birgalikda rivojlanishimiz mumkin.",
            "Tabriklayman! Juda yaxshi boshlang'ich.",
            "Maqsadga erishish uchun har kuni qancha vaqt ajratyapsiz?",
            "Bu maqsadga erishish uchun qanday reja tuzdingiz?",
            "Eng qiyin qismi nima bo'ldi?",
            "Sizning maqsadlaringiz juda ilhomlantiruvchi!",
            "Qanday yutuqlarga erishdingiz?",
            "Bu maqsadni nima uchun tanladingiz?",
            "Sizga kuch va sabr tilayman!",
            "Maqsadga erishish yo'lida qanday to'siqlarga duch keldingiz?",
            "Bu maqsadga erishish uchun qanday o'zgarishlar qildingiz?",
            "Ajoyib g'oya! Sizga omad tilayman!",
            "Bu juda qiziqarli g'oya, men ham shunga o'xshash maqsad qo'ymoqchiman.",
            "Qanday qilib boshladingiz? Maslahatlaringiz bormi?",
            "Davom eting! Maqsadga erishishingizga ishonaman.",
            "Bu maqsadga erishish uchun qanday resurslardan foydalanyapsiz?",
            "Zo'r! Natijalarni kutib qolaman.",
            "Sizning intilishingiz meni ilhomlantirdi.",
            "Qiyinchiliklar bo'ladimi? Ularni qanday yengyapsiz?",
            "Bu maqsad uchun eng muhim qadam nima deb o'ylaysiz?",
            "Men ham bu yo'nalishda ishlayapman, birgalikda rivojlanishimiz mumkin.",
            "Tabriklayman! Juda yaxshi boshlang'ich.",
            "Maqsadga erishish uchun har kuni qancha vaqt ajratyapsiz?",
            "Bu maqsadga erishish uchun qanday reja tuzdingiz?",
            "Eng qiyin qismi nima bo'ldi?",
            "Sizning maqsadlaringiz juda ilhomlantiruvchi!",
            "Qanday yutuqlarga erishdingiz?",
            "Bu maqsadni nima uchun tanladingiz?",
            "Sizga kuch va sabr tilayman!",
            "Maqsadga erishish yo'lida qanday to'siqlarga duch keldingiz?",
            "Bu maqsadga erishish uchun qanday o'zgarishlar qildingiz?",
        ]

        # Har bir maqsadga kamida bitta, ba'zilariga bir nechta izoh qo'shish
        comment_count = 0
        for goal in created_goals:
            # Maqsadni yaratgan foydalanuvchi izoh qoldirishi
            GoalMessage.objects.create(
                goal=goal,
                user=goal.created_by,
                message=random.choice(sample_comments),
                timestamp=timezone.now() - timedelta(minutes=random.randint(1, 60))
            )
            self.stdout.write(self.style.SUCCESS(f"'{goal.title}' maqsadiga izoh qo'shildi ({goal.created_by.username})."))
            comment_count += 1

            # Boshqa tasodifiy foydalanuvchilar ham izoh qoldirishi
            num_additional_comments = random.randint(0, 2) # Har bir maqsadga 0 dan 2 gacha qo'shimcha izoh
            for _ in range(num_additional_comments):
                if comment_count >= 30: # 30+ izoh chegarasiga erishish
                    break
                
                # Tasodifiy foydalanuvchini tanlash (maqsadni yaratgan foydalanuvchidan farqli bo'lishi mumkin)
                comment_user = random.choice(created_users)
                
                GoalMessage.objects.create(
                    goal=goal,
                    user=comment_user,
                    message=random.choice(sample_comments),
                    timestamp=timezone.now() - timedelta(minutes=random.randint(1, 60))
                )
                self.stdout.write(self.style.SUCCESS(f"'{goal.title}' maqsadiga izoh qo'shildi ({comment_user.username})."))
                comment_count += 1
            if comment_count >= 30:
                break
        
        self.stdout.write(self.style.SUCCESS(f'Jami {comment_count} ta Maqsad Izohi yuklandi!'))
        self.stdout.write(self.style.SUCCESS('Barcha ma\'lumotlarni yuklash jarayoni muvaffaqiyatli yakunlandi!'))

