# Stripe API Documentation

**Official Docs:** https://docs.stripe.com/api

## Overview
Stripe is our payment processing platform for handling subscriptions, billing, and payment methods in the Seed Planter API.

## Authentication
```python
import stripe

stripe.api_key = "your-secret-key"  # Set via environment variable
```

## Key Concepts

### Customers
Represents users who can make purchases.
```python
customer = stripe.Customer.create(
    email="customer@example.com",
    metadata={"user_id": "123"}
)
```

### Products & Prices
Define what you're selling.
```python
product = stripe.Product.create(name="Pro Plan")
price = stripe.Price.create(
    product=product.id,
    unit_amount=2000,  # $20.00
    currency="usd",
    recurring={"interval": "month"}
)
```

### Subscriptions
Recurring billing for customers.
```python
subscription = stripe.Subscription.create(
    customer=customer.id,
    items=[{"price": price.id}],
    payment_behavior="default_incomplete",
    expand=["latest_invoice.payment_intent"]
)
```

### Payment Intents
One-time payments.
```python
intent = stripe.PaymentIntent.create(
    amount=2000,
    currency="usd",
    customer=customer.id,
    payment_method_types=["card"]
)
```

## Webhooks
Handle events from Stripe (payment success, subscription updates, etc.)

```python
import stripe

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return {"error": "Invalid payload"}
    except stripe.error.SignatureVerificationError:
        return {"error": "Invalid signature"}
    
    # Handle event types
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        # Handle successful payment
    elif event.type == "customer.subscription.updated":
        subscription = event.data.object
        # Handle subscription update
    
    return {"status": "success"}
```

## Common Event Types
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

## Testing
Use test mode with test cards:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Requires authentication: `4000 0025 0000 3155`

## Error Handling
```python
try:
    charge = stripe.Charge.create(...)
except stripe.error.CardError as e:
    # Card was declined
    pass
except stripe.error.RateLimitError:
    # Too many requests
    pass
except stripe.error.InvalidRequestError:
    # Invalid parameters
    pass
except stripe.error.AuthenticationError:
    # Authentication failed
    pass
except stripe.error.APIConnectionError:
    # Network issue
    pass
except stripe.error.StripeError:
    # Generic error
    pass
```

## Best Practices
1. **Use webhooks** for async events (don't rely on API responses alone)
2. **Idempotency keys** for safe retries
3. **Store Stripe IDs** in your database
4. **Test in test mode** before going live
5. **Handle all webhook events** gracefully
6. **Use metadata** to link Stripe objects to your data

## Environment Variables
```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## API Versions
Stripe uses API versioning. Pin your version for consistency.
Current version used: Check your Stripe Dashboard → Developers → API version

## Resources
- API Reference: https://docs.stripe.com/api
- Python Library: https://github.com/stripe/stripe-python
- Dashboard: https://dashboard.stripe.com
- Testing: https://docs.stripe.com/testing

## Version Used in SeedGPT
```
stripe==7.8.0
```
