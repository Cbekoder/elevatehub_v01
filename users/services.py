
from django.contrib import messages
from users.models import Achievement, UserAchievement

def add_xp_and_check_level_up(request, xp_amount):
    """
    Foydalanuvchiga XP qo'shadi va darajasi oshishini tekshiradi.
    """
    profile = request.user.profile
    profile.xp += xp_amount
    
    # Darajani oshirish mantiqi
    xp_needed = profile.level_up_xp_threshold()
    if profile.xp >= xp_needed:
        profile.level += 1
        profile.xp -= xp_needed # Keyingi daraja uchun XP ni reset qilish
        profile.coins += 50 # Har bir yangi daraja uchun 50 tanga bonus
        messages.success(request, f"🎉 Tabriklaymiz! Siz {profile.level}-darajaga o'tdingiz va 50 tanga bonus oldingiz!")

    profile.save()

def grant_achievement(request, achievement_slug):
    """
    Foydalanuvchiga yutuq beradi (agar u avval olmagan bo'lsa).
    """
    try:
        achievement = Achievement.objects.get(slug=achievement_slug)
        # Foydalanuvchi bu yutuqni avval olmaganligini tekshirish
        if not UserAchievement.objects.filter(user=request.user, achievement=achievement).exists():
            UserAchievement.objects.create(user=request.user, achievement=achievement)
            # Yutuq uchun ball va tangalarni qo'shish
            profile = request.user.profile
            profile.coins += achievement.coin_reward
            profile.save()
            add_xp_and_check_level_up(request, achievement.xp_reward)
            messages.info(request, f"🏆 Yangi yutuq: '{achievement.title}'! Siz {achievement.coin_reward} tanga va {achievement.xp_reward} XP yutib oldingiz.")
    except Achievement.DoesNotExist:
        # Bunday yutuq topilmasa, hech narsa qilmaymiz
        pass
