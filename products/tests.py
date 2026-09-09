from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Enquiry
from products.forms import EnquiryForm
from products.utils import generate_product_whatsapp_url, generate_enquiry_whatsapp_url, get_whatsapp_number


class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Herbal Hair Oil Test",
            description="Nourishing herbal oil test description",
            price=299.00,
            category="Hair Care"
        )

    def test_product_creation_and_auto_slug(self):
        self.assertEqual(self.product.slug, "herbal-hair-oil-test")
        self.assertTrue(self.product.is_available)
        self.assertEqual(str(self.product), "Herbal Hair Oil Test (₹299.00)")

    def test_unique_slug_generation(self):
        duplicate_product = Product.objects.create(
            name="Herbal Hair Oil Test",
            description="Another hair oil",
            price=350.00,
            category="Hair Care"
        )
        self.assertEqual(duplicate_product.slug, "herbal-hair-oil-test-1")


class EnquiryFormTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Ayurvedic Face Pack",
            description="Gentle face pack",
            price=249.00,
            category="Skin Care"
        )

    def test_valid_enquiry_form(self):
        form_data = {
            'name': 'Rahul Sharma',
            'phone': '9876543210',
            'product': self.product.id,
            'message': 'I would like to enquire about bulk order pricing.'
        }
        form = EnquiryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_phone_number(self):
        form_data = {
            'name': 'Rahul Sharma',
            'phone': '12345',  # Invalid phone length
            'product': self.product.id,
            'message': 'Valid message here.'
        }
        form = EnquiryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_invalid_numeric_name(self):
        form_data = {
            'name': '123456',  # Only numbers
            'phone': '9876543210',
            'message': 'Valid message here.'
        }
        form = EnquiryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Herbal Shampoo",
            description="Daily hair shampoo",
            price=349.00,
            category="Hair Care"
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/home.html')
        self.assertIn(self.product, response.context['products'])

    def test_product_detail_view(self):
        response = self.client.get(reverse('product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertEqual(response.context['product'], self.product)

    def test_product_detail_404(self):
        response = self.client.get(reverse('product_detail', kwargs={'slug': 'non-existent-product'}))
        self.assertEqual(response.status_code, 404)

    def test_enquiry_submission(self):
        post_data = {
            'name': 'Ananya Patel',
            'phone': '+919876543210',
            'product': self.product.id,
            'message': 'Is this shampoo safe for daily use?'
        }
        response = self.client.post(reverse('home'), post_data)
        self.assertEqual(Enquiry.objects.count(), 1)
        enquiry = Enquiry.objects.first()
        self.assertRedirects(response, reverse('enquiry_success', kwargs={'enquiry_id': enquiry.id}))


class WhatsAppUtilsTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Ayurvedic Body Oil",
            description="Soothing body oil",
            price=399.00,
            category="Body Care"
        )

    def test_whatsapp_product_url(self):
        url = generate_product_whatsapp_url(self.product)
        number = get_whatsapp_number()
        self.assertIn(f"https://wa.me/{number}?text=", url)
        self.assertIn("Ayurvedic%20Body%20Oil", url)

    def test_whatsapp_enquiry_url(self):
        enquiry = Enquiry.objects.create(
            name="Suresh Kumar",
            phone="9876543210",
            product=self.product,
            message="Please call back."
        )
        url = generate_enquiry_whatsapp_url(enquiry)
        self.assertIn("Suresh%20Kumar", url)
        self.assertIn("Ayurvedic%20Body%20Oil", url)
