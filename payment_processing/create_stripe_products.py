#!/usr/bin/env python3
"""
Create Stripe Products and Prices for Synapse Platform

This script creates all the products and pricing plans in your Stripe account.
"""

import subprocess
import json
import sys

def run_stripe_command(command):
    """Run a Stripe CLI command and return the result."""
    import os
    stripe_exe = os.path.expanduser("~/bin/stripe.exe")
    full_command = f'"{stripe_exe}" {command}'
    
    try:
        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None

def create_product(name, description):
    """Create a product in Stripe."""
    print(f"Creating product: {name}")
    
    command = f'products create --name="{name}" --description="{description}"'
    result = run_stripe_command(command)
    
    if result:
        # Parse the product ID from the output
        lines = result.strip().split('\n')
        for line in lines:
            if line.startswith('id:'):
                product_id = line.split(':')[1].strip()
                print(f"  Created product: {product_id}")
                return product_id
    return None

def create_price(product_id, amount, currency, interval, nickname):
    """Create a price for a product."""
    print(f"  Creating price: {nickname}")
    
    if interval == "month":
        command = f'prices create --product={product_id} --unit-amount={amount} --currency={currency} --recurring[interval]={interval} --nickname="{nickname}"'
    else:  # yearly
        command = f'prices create --product={product_id} --unit-amount={amount} --currency={currency} --recurring[interval]=year --nickname="{nickname}"'
    
    result = run_stripe_command(command)
    
    if result:
        lines = result.strip().split('\n')
        for line in lines:
            if line.startswith('id:'):
                price_id = line.split(':')[1].strip()
                print(f"    Price ID: {price_id}")
                return price_id
    return None

def main():
    print("Creating Synapse Platform Products in Stripe")
    print("=" * 60)
    
    # Define products and their prices
    products = [
        {
            "name": "Synapse Starter",
            "description": "Starter plan with 10,000 API calls, 100 quantum simulations/day, 5 GPU hours",
            "monthly_price": 2900,  # $29.00 in cents
            "yearly_price": 29000,   # $290.00 in cents
        },
        {
            "name": "Synapse Professional",
            "description": "Pro plan with 100,000 API calls, unlimited quantum simulations, 50 GPU hours, AutoML",
            "monthly_price": 9900,   # $99.00
            "yearly_price": 99000,   # $990.00
        },
        {
            "name": "Synapse Enterprise",
            "description": "Enterprise plan with unlimited API calls, 500 GPU hours, distributed training, 24/7 support",
            "monthly_price": 49900,  # $499.00
            "yearly_price": 499000,  # $4,990.00
        },
        {
            "name": "Synapse Quantum Research",
            "description": "Quantum plan with real quantum hardware access, unlimited resources, research support",
            "monthly_price": 199900, # $1,999.00
            "yearly_price": 1999000, # $19,990.00
        }
    ]
    
    price_ids = {}
    
    for product_config in products:
        # Create product
        product_id = create_product(
            product_config["name"],
            product_config["description"]
        )
        
        if product_id:
            # Create monthly price
            monthly_price_id = create_price(
                product_id,
                product_config["monthly_price"],
                "usd",
                "month",
                f"{product_config['name']} - Monthly"
            )
            
            # Create yearly price
            yearly_price_id = create_price(
                product_id,
                product_config["yearly_price"],
                "usd",
                "year",
                f"{product_config['name']} - Yearly"
            )
            
            # Store price IDs
            plan_name = product_config["name"].replace("Synapse ", "").lower()
            price_ids[f"{plan_name}_monthly"] = monthly_price_id
            price_ids[f"{plan_name}_yearly"] = yearly_price_id
        
        print()
    
    # Display all price IDs for .env file
    print("=" * 60)
    print("Add these Price IDs to your .env file:")
    print()
    
    for key, price_id in price_ids.items():
        if price_id:
            env_key = f"PRICE_{key.upper()}"
            print(f"{env_key}={price_id}")
    
    print()
    print("Products and prices created successfully!")
    
    # Save to file for reference
    with open("stripe_price_ids.txt", "w") as f:
        f.write("# Stripe Price IDs for Synapse Platform\n")
        f.write(f"# Created for account: CROWE LOGIC\n\n")
        for key, price_id in price_ids.items():
            if price_id:
                env_key = f"PRICE_{key.upper()}"
                f.write(f"{env_key}={price_id}\n")
    
    print("Price IDs saved to stripe_price_ids.txt")

if __name__ == "__main__":
    main()