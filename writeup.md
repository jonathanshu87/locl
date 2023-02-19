# Inspiration
Meet Lainey! Over the past three years, she has spent over 2,000 hours volunteering with youth who attend under-resourced schools in Washington state. During the sudden onset of the pandemic, the rapid school closures ended the state’s Free and Reduced Lunch program for thousands of children across the state–pushing the burden of purchasing healthy foods onto parents. It suddenly became apparent that many families she worked with heavily relied on Food Stamps, otherwise known as SNAP (Supplemental Nutrition Assistance Program) to purchase the bare necessities. SNAP has gained renown for its positive effects on the livelihoods of lower-income families in the United States. SNAP works by loading a monthly balance onto an EBT card, which functions as a debit card that can only purchase food and other daily essentials.

However, it still has its limitations: to qualify to accept food stamps, stores must sell food in each of the staple food categories. Oftentimes, the only stores that possess the quantities of scale to achieve this are a small set of large chain grocery stores, which lack diverse healthy food options in favor of highly-processed  goods. Not only does this hurt consumers with limited healthy options, it also prevents small, local producers from selling their ethically and sustainably sourced produce to those most in need. 

# What does Locl do?

Locl works to alleviate this obstacle. Namely, it offers a platform where multiple local producers can list their foodstuffs online for shoppers to purchase with their EBT card. This provides a convenient and accessible way for EBT cardholders to access healthy meals, while also promoting better eating habits and supporting local markets and farmers.

When designing our product, the top concerns were ensuring an ethical and sustainable approach to listing produce online for low-income shoppers. To use Locl, users would require an electronic device and an internet connection-ultimately limiting access within our target audience. Beyond this, we recognized that certain produce items or markets could be displayed disproportionally in comparison to others, which could create imbalances and inequities between all the stakeholders involved.

## EBT Support

Shoppers can convert their EBT balance into Locl credits. From there, they can spend their credits buying produce from our set of carefully curated suppliers. To prevent fraud, each vendor is carefully evaluated to ensure they sell ethically sourced foodstuffs. Thus, shoppers can only spend their Locl credits on foodstuffs.

## Bank-less payment

Because low-income shoppers may not have access to a bank account, we've used Checkbook.io's virtual credit cards and direct deposit to facilitate payments between shoppers and vendors.

## Producer accessibility

By listing multiple vendors on one platform, Locl is able to circumvent the initial problems of scale. Rather than each vendor being its own store, we consolidate them all into one large store, thereby easily meeting all required food categories.

## Recognizable marketplace

To improve the ease of use, Locl's interface is carefully crafted to emulate other popular marketplace applications such as Facebook Marketplace and Craigslist. Because shoppers will already be accustomed to our app, it'll far improve the overall user experience.

# How we built it

Locl revolves around a web app interface to allow shoppers and vendors to buy and sell produce.

## Flask

The crux of Locl centers on our Flask server. From there, we use ```requests``` and ```render_templates()``` to populate our website with GET and POST requests. 

## Supabase

We use Supabase and PostgreSQL to store our product, store, virtual credit card, and user information. Because Flask is a Python library, we use Supabase's community managed Python library to insert and update data.

## Checkbook.io

We use Checkbook.io's Payfac API to create transactions between shoppers and vendors. First, shoppers deposit credits into their Locl account from the EBT card. The EBT funds are later redeemed with the state government by Locl. Next, each time a shopper decides to purchase a good, our ```owner``` user will transfer funds to the desired vendor's virtual credit card. From there, vendors can spend their funds as if it were a pre-paid debit card.

# Challenges we encountered

Because we were all new to using these APIs, we were initially unclear about what actions they could suppport. For example, we wanted to use You.com API to build our marketplace. However, it soon became apparent that we couldn't embed their API into our static HTML page as we'd assume. Thus, we had to pivot to creating our own cards with Jinja.

# Looking forward

Of course, there are still a few features we'd like to include in a longer timeframe.
- a search and filtering system to show shoppers their preferred goods.
- an automated redemption system with the state government for EBT.
- improved security and encryption for all API calls and database queries.