import os
import django
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ayurvedic_products.settings')
django.setup()

from products.models import Product

def create_placeholder_image(filename, text, bg_color, accent_color):
    media_dir = os.path.join(os.path.dirname(__file__), 'media', 'products')
    static_img_dir = os.path.join(os.path.dirname(__file__), 'products', 'static', 'products', 'images')
    os.makedirs(media_dir, exist_ok=True)
    os.makedirs(static_img_dir, exist_ok=True)

    img = Image.new('RGB', (800, 600), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Draw subtle background pattern / circles
    draw.ellipse([(-100, -100), (300, 300)], fill=(255, 255, 255, 30))
    draw.ellipse([(500, 300), (900, 700)], fill=(255, 255, 255, 30))

    # Decorative inner frame
    draw.rectangle([(40, 40), (760, 560)], outline=accent_color, width=4)
    draw.rectangle([(50, 50), (750, 550)], outline=accent_color, width=1)

    # Title text
    try:
        font_title = ImageFont.truetype("arial.ttf", 42)
        font_sub = ImageFont.truetype("arial.ttf", 22)
    except IOError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Center text
    bbox = draw.textbbox((0, 0), text, font=font_title)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((800 - w) / 2, 230), text, fill=accent_color, font=font_title)

    sub_text = "HerbaCare Authentic Ayurveda"
    sub_bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = sub_bbox[2] - sub_bbox[0]
    draw.text(((800 - sw) / 2, 300), sub_text, fill=(80, 90, 80), font=font_sub)

    # Save to media/products
    file_path = os.path.join(media_dir, filename)
    img.save(file_path, format='JPEG', quality=95)
    
    # Save hero or static image if hero
    if filename == 'hero_ayurveda.jpg':
        hero_path = os.path.join(static_img_dir, filename)
        img.save(hero_path, format='JPEG', quality=95)
    elif filename == 'placeholder_product.jpg':
        ph_path = os.path.join(static_img_dir, filename)
        img.save(ph_path, format='JPEG', quality=95)

    return f"products/{filename}"

def seed():
    print("Generating media image files...")
    img_hair_oil = create_placeholder_image('herbal_hair_oil.jpg', 'Herbal Hair Oil', (234, 241, 231), (46, 90, 39))
    img_face_pack = create_placeholder_image('ayurvedic_face_pack.jpg', 'Ayurvedic Face Pack', (245, 238, 225), (140, 109, 70))
    img_shampoo = create_placeholder_image('herbal_shampoo.jpg', 'Herbal Shampoo', (225, 238, 238), (30, 85, 80))
    img_body_oil = create_placeholder_image('ayurvedic_body_oil.jpg', 'Ayurvedic Body Oil', (243, 234, 220), (160, 110, 50))
    
    create_placeholder_image('hero_ayurveda.jpg', 'HerbaCare Ayurvedic Collection', (234, 241, 231), (46, 90, 39))
    create_placeholder_image('placeholder_product.jpg', 'HerbaCare Product', (240, 240, 240), (100, 100, 100))

    sample_products = [
        {
            'name': 'Herbal Hair Oil',
            'category': 'Hair Care',
            'description': 'A nourishing herbal hair oil inspired by traditional Ayurvedic hair-care practices. Formulated with Bhringraj, Amla, and Sesame oil to promote healthy hair growth and scalp nourishment.',
            'price': 299.00,
            'image': img_hair_oil,
            'is_available': True,
        },
        {
            'name': 'Ayurvedic Face Pack',
            'category': 'Skin Care',
            'description': 'A gentle herbal face pack designed for a refreshing and natural skincare routine. Packed with Chandan (Sandalwood), Neem, and Turmeric to cleanse pores and brighten complexion.',
            'price': 249.00,
            'image': img_face_pack,
            'is_available': True,
        },
        {
            'name': 'Herbal Shampoo',
            'category': 'Hair Care',
            'description': 'A herbal shampoo formulated for a refreshing everyday hair-care experience. Contains Shikakai, Reetha, and Hibiscus to cleanse gently without stripping natural moisture.',
            'price': 349.00,
            'image': img_shampoo,
            'is_available': True,
        },
        {
            'name': 'Ayurvedic Body Oil',
            'category': 'Body Care',
            'description': 'A soothing herbal body oil designed for a relaxing personal-care routine. Infused with Ashwagandha and Bala to rejuvenate skin and relax tired muscles during Abhyanga massage.',
            'price': 399.00,
            'image': img_body_oil,
            'is_available': True,
        },
    ]

    print("Seeding database with sample products...")
    for item in sample_products:
        product, created = Product.objects.get_or_create(
            name=item['name'],
            defaults=item
        )
        if created:
            print(f"Created product: {product.name} (INR {product.price})")
        else:
            # Update image path
            product.image = item['image']
            product.description = item['description']
            product.price = item['price']
            product.category = item['category']
            product.save()
            print(f"Updated product: {product.name}")

    print("Seed process completed successfully!")

if __name__ == '__main__':
    seed()

