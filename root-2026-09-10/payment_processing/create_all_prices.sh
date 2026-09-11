#!/bin/bash

# Create all prices for Synapse Platform products

echo "Creating all prices for Synapse Platform..."
echo "============================================"

# Starter Plan
echo "Creating Starter prices..."
~/bin/stripe.exe prices create --product prod_T2ZEZF78sSMWRK --unit-amount 29000 --currency usd -d "recurring[interval]=year" -d "nickname=Synapse Starter - Yearly"

# Professional Plan
echo "Creating Professional prices..."
~/bin/stripe.exe prices create --product prod_T2ZE6RlHInI0Iz --unit-amount 9900 --currency usd -d "recurring[interval]=month" -d "nickname=Synapse Professional - Monthly"
~/bin/stripe.exe prices create --product prod_T2ZE6RlHInI0Iz --unit-amount 99000 --currency usd -d "recurring[interval]=year" -d "nickname=Synapse Professional - Yearly"

# Enterprise Plan
echo "Creating Enterprise prices..."
~/bin/stripe.exe prices create --product prod_T2ZEQDfwyCNVEx --unit-amount 49900 --currency usd -d "recurring[interval]=month" -d "nickname=Synapse Enterprise - Monthly"
~/bin/stripe.exe prices create --product prod_T2ZEQDfwyCNVEx --unit-amount 499000 --currency usd -d "recurring[interval]=year" -d "nickname=Synapse Enterprise - Yearly"

# Quantum Research Plan
echo "Creating Quantum Research prices..."
~/bin/stripe.exe prices create --product prod_T2ZEzVMQGyxPKu --unit-amount 199900 --currency usd -d "recurring[interval]=month" -d "nickname=Synapse Quantum Research - Monthly"
~/bin/stripe.exe prices create --product prod_T2ZEzVMQGyxPKu --unit-amount 1999000 --currency usd -d "recurring[interval]=year" -d "nickname=Synapse Quantum Research - Yearly"

echo "All prices created successfully!"