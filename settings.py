class Settings:

    plan = {
        'section': 'Model%20Guidance',
        'model': 'GFS',
        'area':
            {
                'NAMER': [],
                'CONUS': [],
            },
        'product_count': 5,
        'hour_count': 1,
    }

    compare = {
        'box_color': (102, 102, 102),  # frame color of the box containing the image
        'padding_offset': [70, 45, 50, 50]  # to ignore header and footer text in the image - comment out if not needed
    }
