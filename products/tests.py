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


class CustomerAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(
            username='testcustomer',
            email='customer@example.com',
            password='TestPassword123!',
            first_name='Rahul',
            last_name='Sharma'
        )
        self.product = Product.objects.create(
            name="Herbal Hair Oil Test",
            description="Nourishing hair oil",
            price=299.00,
            category="Hair Care"
        )

    def test_registration_view(self):
        post_data = {
            'username': 'newcustomer',
            'first_name': 'Ananya',
            'last_name': 'Roy',
            'email': 'ananya@example.com',
            'password1': 'NewPassword123!',
            'password2': 'NewPassword123!',
        }
        response = self.client.post(reverse('register'), post_data)
        self.assertRedirects(response, reverse('my_enquiries'))
        from django.contrib.auth.models import User
        self.assertTrue(User.objects.filter(username='newcustomer').exists())

    def test_login_and_logout_view(self):
        login_data = {
            'username': 'testcustomer',
            'password': 'TestPassword123!',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, reverse('my_enquiries'))

        logout_response = self.client.get(reverse('logout'))
        self.assertRedirects(logout_response, reverse('home'))

    def test_authenticated_enquiry_linking(self):
        self.client.login(username='testcustomer', password='TestPassword123!')
        post_data = {
            'name': 'Rahul Sharma',
            'phone': '9876543210',
            'product': self.product.id,
            'message': 'Enquiry from logged in user.'
        }
        response = self.client.post(reverse('home'), post_data)
        self.assertEqual(Enquiry.objects.count(), 1)
        enquiry = Enquiry.objects.first()
        self.assertEqual(enquiry.user, self.user)

    def test_my_enquiries_protected_view(self):
        # Unauthenticated access should redirect to login
        unauth_response = self.client.get(reverse('my_enquiries'))
        self.assertRedirects(unauth_response, f"{reverse('login')}?next={reverse('my_enquiries')}")

        # Authenticated access
        self.client.login(username='testcustomer', password='TestPassword123!')
        auth_response = self.client.get(reverse('my_enquiries'))
        self.assertEqual(auth_response.status_code, 200)
        self.assertTemplateUsed(auth_response, 'products/my_enquiries.html')


class CartSystemTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.p1 = Product.objects.create(
            name="Kumkumadi Face Serum",
            description="Glowing serum",
            price=499.00,
            category="Skin Care"
        )
        self.p2 = Product.objects.create(
            name="Triphala Tea",
            description="Digestive tea",
            price=199.00,
            category="Herbal Care"
        )

    def test_cart_add_and_count(self):
        # Add p1 (qty 2)
        response = self.client.post(reverse('cart_add', kwargs={'product_id': self.p1.id}), {'quantity': 2})
        self.assertRedirects(response, reverse('cart_detail'))

        # Add p2 (qty 1)
        self.client.post(reverse('cart_add', kwargs={'product_id': self.p2.id}), {'quantity': 1})

        # Verify cart view
        cart_response = self.client.get(reverse('cart_detail'))
        self.assertEqual(cart_response.status_code, 200)
        self.assertEqual(len(cart_response.context['cart']), 3)  # 2 + 1 = 3 items
        self.assertEqual(cart_response.context['cart'].get_total_price(), 499.00 * 2 + 199.00)

    def test_cart_update_and_remove(self):
        self.client.post(reverse('cart_add', kwargs={'product_id': self.p1.id}), {'quantity': 1})
        
        # Update quantity to 5
        self.client.post(reverse('cart_update', kwargs={'product_id': self.p1.id}), {'quantity': 5})
        cart_response = self.client.get(reverse('cart_detail'))
        self.assertEqual(len(cart_response.context['cart']), 5)

        # Remove item
        self.client.get(reverse('cart_remove', kwargs={'product_id': self.p1.id}))
        cart_response_after = self.client.get(reverse('cart_detail'))
        self.assertEqual(len(cart_response_after.context['cart']), 0)

    def test_cart_checkout_whatsapp(self):
        self.client.post(reverse('cart_add', kwargs={'product_id': self.p1.id}), {'quantity': 1})
        response = self.client.get(reverse('cart_checkout_whatsapp'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('https://wa.me/', response.url)
        self.assertIn('Kumkumadi%20Face%20Serum', response.url)

    def test_cart_checkout_enquiry(self):
        self.client.post(reverse('cart_add', kwargs={'product_id': self.p1.id}), {'quantity': 2})
        response = self.client.get(reverse('cart_checkout_enquiry'))
        self.assertEqual(Enquiry.objects.count(), 1)
        enquiry = Enquiry.objects.first()
        self.assertIn("Kumkumadi Face Serum", enquiry.message)
        self.assertRedirects(response, reverse('enquiry_success', kwargs={'enquiry_id': enquiry.id}))

    def test_cart_persistence_across_login_logout(self):
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='persistentuser', password='Password123!')
        
        # Log in and add product to cart
        self.client.login(username='persistentuser', password='Password123!')
        self.client.post(reverse('cart_add', kwargs={'product_id': self.p1.id}), {'quantity': 3})
        
        # Log out (flushes session)
        self.client.get(reverse('logout'))
        
        # Cart should be empty for guest after logout
        guest_cart = self.client.get(reverse('cart_detail'))
        self.assertEqual(len(guest_cart.context['cart']), 0)

        # Log back in: cart items should be restored automatically from DB!
        self.client.login(username='persistentuser', password='Password123!')
        restored_cart = self.client.get(reverse('cart_detail'))
        self.assertEqual(len(restored_cart.context['cart']), 3)

    def test_guest_cart_merges_on_login(self):
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='mergeuser', password='Password123!')
        
        # Add item as guest
        self.client.post(reverse('cart_add', kwargs={'product_id': self.p2.id}), {'quantity': 2})
        
        # Log in via login view
        self.client.post(reverse('login'), {'username': 'mergeuser', 'password': 'Password123!'})
        
        # Cart should retain the guest item after logging in
        logged_in_cart = self.client.get(reverse('cart_detail'))
        self.assertEqual(len(logged_in_cart.context['cart']), 2)




