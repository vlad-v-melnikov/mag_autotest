class Settings:

    HOUR_SAMPLE_SIZE = 1

    plan = {
        'section': 'Model%20Guidance',
        'model': 'GFS',
        'area':
            {
                'NAMER': ['precip_p01'],
            },
        'product_number': 0,
        'area_number': 0,
    }

    compare = {
        'box_color': (102, 102, 102),  # frame color of the box containing the image
        # 'padding_offset': 50,  # needed to ignore header and footer text in the image - comment it out if not needed
    }

    entire_thing = {
        'GFS':
        {
            'section': 'Model%20Guidance',
            'area':
                {
                    'NAMER': ['precip_p01'],
                },
            'product_number': 0,
            'area_number': 0,
        }
    }
