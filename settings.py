class Settings:

    plan = {
        'GFS':
            {
            'section': 'Model%20Guidance',
            'model': 'GFS',
            'product_count': 1,
            'hour_count': 1,
            'area_count': 1,
            },
        'GEFS-SPAG':
            {
                'section': 'Model%20Guidance',
                'model': 'GEFS-SPAG',
                'product_count': 1,
                'hour_count': 1,
                'area_count': 1,
            }
        }

    compare = {
        'box_color': (102, 102, 102),  # frame color of the box containing the image
        'padding_offset': [70, 45, 50, 50]  # to ignore header and footer text in the image - comment out if not needed
    }

    sites = {
        'test': "https://magtest.ncep.noaa.gov",
        'prod': "https://mag.ncep.noaa.gov",
    }
