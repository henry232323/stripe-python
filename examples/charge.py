import os
import asyncio

import stripe

loop = asyncio.get_event_loop()
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

async def run_charge():
    print("Attempting charge...")

    resp = await stripe.Charge.create(
        amount=200,
        currency="usd",
        card="tok_visa",
        description="customer@gmail.com",
    )

    print("Success: %r" % (resp))

loop.run_until_complete(run_charge())
