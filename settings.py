class Settings:

    HOUR_SAMPLE_SIZE = 1

    plan = {
        'section': 'Model%20Guidance',
        'model': 'GFS',
        'area':
            {
                'NAMER': ['precip_p01'],
            }
    }

    compare = {
        'box_color': (102, 102, 102),  # frame color of the box containing the image
        'padding_offset': 50,  # needed to ignore header and footer text in the image
    }
