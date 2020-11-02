class Settings:

    sites = {
        'test': "https://mag.ncep.noaa.gov",
        'prod': "https://mag.ncep.noaa.gov",

        'area_from': 'test',
        'cycle_from': 'test',
        'products_from': 'prod',
        'cluster_from': 'prod',

        'order_of_iteration': ['test', 'prod'],
        'today_only': False,
    }

    driver = 'Firefox'
    plan = {
        'STORM-TRACKS':
            {
                'area': {
                    'ALASKA': [],
                    'CONUS': [],
                },
                'section': 'Model Guidance',
                'model': 'STORM-TRACKS',
                'area_count': 0,
                'product_count': 2,
                'hour_count': 2,
            },
        'PANELS':
            {
                'section': 'Model Guidance',
                'model': 'PANELS',
                'area_count': 2,
                'product_count': 2,
                'hour_count': 1,
            },
        'SREF-CLUSTER':
            {
                'section': 'Model Guidance',
                'model': 'SREF-CLUSTER',
                'area_count': 3,
                'product_count': 1,
                'hour_count': 1,
                'cluster_count': 1,
            },
        'GFS':
            {
                'section': 'Model Guidance',
                'model': 'GFS',
                'area_count': 2,
                'product_count': 2,
                'hour_count': 1,
            },
        'GEFS-SPAG':
            {
                'section': 'Model Guidance',
                'model': 'GEFS-SPAG',
                'area_count': 1,
                'product_count': 3,
                'hour_count': 1,
            },
        'GEFS-MEAN-SPRD':
            {
                'section': 'Model Guidance',
                'model': 'GEFS-MEAN-SPRD',
                'area_count': 1,
                'product_count': 3,
                'hour_count': 1,
            },
        'NAEFS':
            {
                'section': 'Model Guidance',
                'model': 'NAEFS',
                'area_count': 1,
                'product_count': 3,
                'hour_count': 1,
            },
        'NAM':
            {
                'section': 'Model Guidance',
                'model': 'NAM',
                'area_count': 1,
                'product_count': 3,
                'hour_count': 1,
            },
        'NAM-HIRES':
            {
                'section': 'Model Guidance',
                'model': 'NAM-HIRES',
                'area_count': 2,
                'product_count': 5,
                'hour_count': 1,
            },
        'FIREWX':
            {
                'section': 'Model Guidance',
                'model': 'FIREWX',
                'area_count': 1,
                'product_count': 5,
                'hour_count': 1,
            },
        'RAP':
            {
                'section': 'Model Guidance',
                'model': 'RAP',
                'area_count': 1,
                'product_count': 3,
                'hour_count': 1,
            },
        'HRRR':
            {
                'section': 'Model Guidance',
                'area':
                    {
                        'CONUS': [],
                        'ALASKA': [],
                        'US-NC': [],
                    },
                'model': 'HRRR',
                'area_count': 0,
                'product_count': 2,
                'hour_count': 1,
            },
        'HRW-ARW':
            {
                'section': 'Model Guidance',
                'model': 'HRW-ARW',
                'area_count': 1,
                'product_count': 3,
                'hour_count': 1,
            },
        'HRW-ARW2':
            {
                'section': 'Model Guidance',
                'model': 'HRW-ARW2',
                'area_count': 1,
                'product_count': 3,
                'hour_count': 1,
            },
        'SREF':
            {
                'section': 'Model Guidance',
                'model': 'SREF',
                'area_count': 1,
                'product_count': 3,
                'hour_count': 1,
            },
        'HREF':
            {
                'section': 'Model Guidance',
                'model': 'HREF',
                'area_count': 1,
                'product_count': 3,
                'hour_count': 1,
            },
        'NBM':
            {
                'section': 'Model Guidance',
                'model': 'NBM',
                'area_count': 1,
                'product_count': 3,
                'hour_count': 1,
            },
        'WW3':
            {
                'section': 'Model Guidance',
                'model': 'WW3',
                'area_count': 1,
                'product_count': 3,
                'hour_count': 1,
            },
        'ESTOFS':
            {
                'section': 'Model Guidance',
                'model': 'ESTOFS',
                'area_count': 1,
                'product_count': 1,
                'hour_count': 1,
            },
        'ICE-DRIFT':
            {
                'section': 'Model Guidance',
                'model': 'ICE-DRIFT',
                'area_count': 1,
                'product_count': 1,
                'hour_count': 1,
            },
        }

    compare = {
        'box_color': (102, 102, 102),  # frame color of the box containing the image
        'padding_offset': [70, 70, 50, 120],  # from: [left, top, right, bottom] sides of the image box
        'use_padding': False,
    }


    delays = {}

