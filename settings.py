class Settings:

    compare = {
        'box_color': (102, 102, 102),  # frame color of the box containing the image
        'padding_offset': [70, 70, 50, 120],  # from: [left, top, right, bottom] sides of the image box
        'use_padding': False,
    }

    delays = {}
    plan = {
        'SREF-CLUSTER':
            {
                'section': 'Model%20Guidance',
                'model': 'SREF-CLUSTER',
                'product_count': 1,
                'hour_count': 3,
                'area_count': 1,
                'cluster_count': 1,
            },
        'GFS':
        {
            'area':
                {
                    'NAMER': ['precip_p01']
                },
            'section': 'Model%20Guidance',
            'model': 'GFS',
            'product_count': 3,
            'hour_count': 1,
            'area_count': 1,
        },
        'GEFS-SPAG':
            {
                'section': 'Model%20Guidance',
                'model': 'GEFS-SPAG',
                'product_count': 3,
                'hour_count': 1,
                'area_count': 1,
            },
        'GEFS-MEAN-SPRD':
            {
                'section': 'Model%20Guidance',
                'model': 'GEFS-MEAN-SPRD',
                'product_count': 3,
                'hour_count': 1,
                'area_count': 1,
            },
        'NAEFS':
            {
                'section': 'Model%20Guidance',
                'model': 'NAEFS',
                'product_count': 3,
                'hour_count': 1,
                'area_count': 1,
            },
        'NAM':
            {
                'section': 'Model%20Guidance',
                'model': 'NAM',
                'product_count': 3,
                'hour_count': 1,
                'area_count': 1,
            },
        'NAM-HIRES':
            {
                'section': 'Model%20Guidance',
                'model': 'NAM-HIRES',
                'product_count': 5,
                'hour_count': 1,
                'area_count': 2,
            },
        'FIREWX':
            {
                'section': 'Model%20Guidance',
                'model': 'FIREWX',
                'product_count': 5,
                'hour_count': 1,
                'area_count': 1,
            },
        'RAP':
            {
                'section': 'Model%20Guidance',
                'model': 'RAP',
                'product_count': 3,
                'hour_count': 1,
                'area_count': 1,
            },
        'HRRR':
            {
                'section': 'Model%20Guidance',
                'area':
                    {
                        'CONUS':['precip_p01', '500_vort_ht,1000_500_thick,700_rh_ht,850_temp_ht']
                    },
                'cycle': '2020102309UTC',
                'model': 'HRRR',
                'product_count': 3,
                'hour_count': 1,
                'area_count': 1,
            },
        'HRW-ARW':
            {
                'section': 'Model%20Guidance',
                'model': 'HRW-ARW',
                'product_count': 3,
                'hour_count': 1,
                'area_count': 1,
            },
        'HRW-ARW2':
            {
                'section': 'Model%20Guidance',
                'model': 'HRW-ARW2',
                'product_count': 3,
                'hour_count': 1,
                'area_count': 1,
            },
        'SREF':
            {
                'section': 'Model%20Guidance',
                'model': 'SREF',
                'product_count': 3,
                'hour_count': 1,
                'area_count': 1,
            },
        'HREF':
            {
                'section': 'Model%20Guidance',
                'model': 'HREF',
                'product_count': 3,
                'hour_count': 1,
                'area_count': 1,
            },
        'NBM':
            {
                'section': 'Model%20Guidance',
                'model': 'NBM',
                'product_count': 3,
                'hour_count': 1,
                'area_count': 1,
            },
        'ESTOFS':
            {
                'section': 'Model%20Guidance',
                'model': 'ESTOFS',
                'product_count': 2,
                'hour_count': 1,
                'area_count': 1,
            },
        'ICE-DRIFT':
            {
                'section': 'Model%20Guidance',
                'model': 'ICE-DRIFT',
                'product_count': 1,
                'hour_count': 1,
                'area_count': 1,
            },
        }

    sites = {
        'test': "https://magtest.ncep.noaa.gov",
        'prod': "https://mag.ncep.noaa.gov",

        'area_from': 'prod',
        'cycle_from': 'test',
        'products_from': 'prod',
        'cluster_from': 'prod',

        'order_of_iteration': ['test', 'prod']
    }

    driver = 'Firefox'

