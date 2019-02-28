AWS Price Tools
===============

Some tools for working with the [AWS Price List API](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html).

Examples
--------

* Get spot prices for all GPU/deep learning instance types in all EU regions:

    ```
    $ python ec2_price.py -r 'eu-*' -t 'g*' -t 'p*' --current-only --format=html > derp.html
    ```
