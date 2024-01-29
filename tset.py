# import re

# pattern = re.compile(r'\d+')
# def get_odometer(text: str) -> int:
#     match = pattern.search(text)
#     return int(match.group()) if match else None

# print(get_odometer(' 456 joj'))
data = [{'car_number': 'DI 0277 YA',
 'car_vin': '5YJYGDEE3MF264394',
 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/tesla_model-y__534351796f.jpg',
 'images_count': 28,
 'odometer': 17,
 'phone_number': '+38(063) 505 65 05',
 'price_usd': 36000,
 'rid': '35956645',
 'title': 'Tesla Model Y 2021',
 'url': 'https://auto.ria.com/uk/auto_tesla_model_y_35956645.html',
 'username': 'Євген' },
{'car_number': 'AI 5059 BO',
 'car_vin': 'WDB2030161A316924',
 'image_url': 'https://cdn3.riastatic.com/photosnew/auto/photo/mercedes-benz_c-class__534358758f.jpg',
 'images_count': 41,
 'odometer': 261,
 'phone_number': '+38(068) 599 99 59',
 'price_usd': 5999,
 'rid': '35956822',
 'title': 'Mercedes-Benz C-Class 2002',
 'url': 'https://auto.ria.com/uk/auto_mercedes_benz_c_class_35956822.html',
 'username': 'Сергей Cергеевич' },
{'car_number': 'AI 2075 PO',
 'car_vin': 'WVWZZZ3CZKE052050',
 'image_url': 'https://cdn2.riastatic.com/photosnew/auto/photo/volkswagen_passat__531218402f.jpg',
 'images_count': 28,
 'odometer': 126,
 'phone_number': '+38(099) 537 75 00',
 'price_usd': 29999,
 'rid': '35839607',
 'title': 'Volkswagen Passat 2018',
 'url': 'https://auto.ria.com/uk/auto_volkswagen_passat_35839607.html',
 'username': 'Максим' },
{'car_number': None,
 'car_vin': None,
 'image_url': 'https://cdn4.riastatic.com/photosnew/auto/photo/schmidt_swingo__534323179f.jpg',
 'images_count': 6,
 'odometer': 101,
 'phone_number': '+38(067) 605 55 88',
 'price_usd': 7000,
 'rid': '35953353',
 'title': 'SCHMIDT Swingo 2007',
 'url': 'https://auto.ria.com/uk/auto_schmidt_swingo_35953353.html',
 'username': 'Вася Феде' },
{'car_number': None,
 'car_vin': 'WBD9066331S902515',
 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/mercedes-benz_sprinter__534357686f.jpg',
 'images_count': 23,
 'odometer': 341,
 'phone_number': '+38(097) 255 10 60',
 'price_usd': 29900,
 'rid': '35956846',
 'title': 'Mercedes-Benz Sprinter 2014',
 'url': 'https://auto.ria.com/uk/auto_mercedes_benz_sprinter_35956846.html',
 'username': 'Олександр' },
{'car_number': 'AE 2493 OO',
 'car_vin': 'SJNFHAJ10U1196177',
 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/nissan_qashqai__524080070f.jpg',
 'images_count': 17,
 'odometer': 225,
 'phone_number': '+38(067) 567 05 53',
 'price_usd': 7650,
 'rid': '35573391',
 'title': 'Nissan Qashqai 2008',
 'url': 'https://auto.ria.com/uk/auto_nissan_qashqai_35573391.html',
 'username': 'Георгий Юрьевич' },
{'car_number': 'BH 2600 TX',
 'car_vin': 'JMBLTCX3A9U005135',
 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/mitsubishi_lancer__534352360f.jpg',
 'images_count': 15,
 'odometer': 166,
 'phone_number': '+38(098) 729 90 37',
 'price_usd': 7900,
 'rid': '35956583',
 'title': 'Mitsubishi Lancer 2009',
 'url': 'https://auto.ria.com/uk/auto_mitsubishi_lancer_35956583.html',
 'username': 'Валик Нейков' },
{'car_number': None,
 'car_vin': 'WMA06XZZ4GP071974',
 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/man_tgx__534363750f.jpg',
 'images_count': 19,
 'odometer': 679,
 'phone_number': '+38(066) 178 78 55',
 'price_usd': 33500,
 'rid': '35956920',
 'title': 'MAN TGX 2015',
 'url': 'https://auto.ria.com/uk/auto_man_tgx_35956920.html',
 'username': 'Валентин' },
{'car_number': None,
 'car_vin': 'KNACC81GFN5138379',
 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/kia_niro__534353111f.jpg',
 'images_count': 42,
 'odometer': 22,
 'phone_number': '+38(063) 806 29 31',
 'price_usd': 32777,
 'rid': '35956716',
 'title': 'Kia Niro 2021',
 'url': 'https://auto.ria.com/uk/auto_kia_niro_35956716.html',
 'username': 'Freshauto' },
{'car_number': None,
 'car_vin': 'WVWHN7AN9CE522978',
 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/volkswagen_cc-passat-cc__534358181f.jpg',
 'images_count': 25,
 'odometer': 225,
 'phone_number': '+38(093) 334 54 67',
 'price_usd': 9000,
 'rid': '35956851',
 'title': 'Volkswagen CC / Passat CC 2011',
 'url': 'https://auto.ria.com/uk/auto_volkswagen_cc_passat_cc_35956851.html',
 'username': 'Яніс' },

  

  

{'car_number': 'BK 0743 IC',
 'car_vin': 'VF7MBRHYB65571508',
 'image_url': 'https://cdn3.riastatic.com/photosnew/auto/photo/citroen_berlingo__534352838f.jpg',
 'images_count': 14,
 'odometer': 230,
 'phone_number': '+38(067) 251 88 98',
 'price_usd': 2750,
 'rid': '35956802',
 'title': 'Citroen Berlingo 2001',
 'url': 'https://auto.ria.com/uk/auto_citroen_berlingo_35956802.html',
 'username': 'Дмитро Васильович Боровець' },
{'car_number': 'AX 5302 MC',
 'car_vin': 'VF7GBRHYB94155935',
 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/citroen_berlingo__534352190f.jpg',
 'images_count': 14,
 'odometer': 337,
 'phone_number': '+38(096) 736 36 95',
 'price_usd': 1900,
 'rid': '35956532',
 'title': 'Citroen Berlingo 2005',
 'url': 'https://auto.ria.com/uk/auto_citroen_berlingo_35956532.html',
 'username': 'Роман Цап' },
{'car_number': 'AI 2132 YA',
 'car_vin': '5YJ3E1EC0LF784550',
 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/tesla_model-3__529760641f.jpg',
 'images_count': 26,
 'odometer': 23,
 'phone_number': '+38(063) 602 15 18',
 'price_usd': 33999,
 'rid': '35782909',
 'title': 'Tesla Model 3 2020',
 'url': 'https://auto.ria.com/uk/auto_tesla_model_3_35782909.html',
 'username': 'Всеволод Медяник' },
{'car_number': 'AA 8080 MT',
 'car_vin': 'JN1TDNJ50U0601766',
 'image_url': 'https://cdn3.riastatic.com/photosnew/auto/photo/infiniti_ex-25__530282498f.jpg',
 'images_count': 45,
 'odometer': 167,
 'phone_number': '+38(067) 173 85 55',
 'price_usd': 14900,
 'rid': '35804322',
 'title': 'Infiniti EX 25 2012',
 'url': 'https://auto.ria.com/uk/auto_infiniti_ex_25_35804322.html',
 'username': 'Car City' },
{'car_number': 'AX 5516 MH',
 'car_vin': 'WVWZZZ3CxCExxxx01',
 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/volkswagen_passat__532565345f.jpg',
 'images_count': 50,
 'odometer': 208,
 'phone_number': '+38(096) 318 14 40',
 'price_usd': 10300,
 'rid': '35889427',
 'title': 'Volkswagen Passat 2012',
 'url': 'https://auto.ria.com/uk/auto_volkswagen_passat_35889427.html',
 'username': 'Слава Маковський' },
{'car_number': None,
 'car_vin': None,
 'image_url': 'https://cdn2.riastatic.com/photosnew/auto/photo/claas_lexion-560__530773912f.jpg',
 'images_count': 18,
 'odometer': 9,
 'phone_number': '+38(097) 111 69 44',
 'price_usd': 85000,
 'rid': '35822158',
 'title': 'Claas Lexion 560 2010',
 'url': 'https://auto.ria.com/uk/auto_claas_lexion_560_35822158.html',
 'username': 'Volodymyr Biluhin' },
{'car_number': 'AA 1880 HA',
 'car_vin': 'KMHDM46BP4U743396',
 'image_url': 'https://cdn2.riastatic.com/photosnew/auto/photo/hyundai_elantra__534350417f.jpg',
 'images_count': 16,
 'odometer': 230,
 'phone_number': '+38(095) 223 48 44',
 'price_usd': 3500,
 'rid': '35956463',
 'title': 'Hyundai Elantra 2003',
 'url': 'https://auto.ria.com/uk/auto_hyundai_elantra_35956463.html',
 'username': 'Ім’я не вказане' },
{'car_number': None,
 'car_vin': 'WBA7U61050BM62592',
 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/bmw_7-series__516509940f.jpg',
 'images_count': 109,
 'odometer': 127,
 'phone_number': '+38(098) 585 76 67',
 'price_usd': 73900,
 'rid': '35286710',
 'title': 'BMW 7 Series 2019',
 'url': 'https://auto.ria.com/uk/auto_bmw_7_series_35286710.html',
 'username': 'LUX cars' },
{'car_number': 'CA 0829 ZA',
 'car_vin': 'VF1AGVYAx51xxxx05',
 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/renault_zoe__502835301f.jpg',
 'images_count': 27,
 'odometer': 95,
 'phone_number': '+38(063) 557 21 93',
 'price_usd': 7800,
 'rid': '34741617',
 'title': 'Renault Zoe 2014',
 'url': 'https://auto.ria.com/uk/auto_renault_zoe_34741617.html',
 'username': 'Богдан' },
{'car_number': 'AE 7932 TE',
 'car_vin': 'WBA4B3C5xFDxxxx75',
 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/bmw_4-series-gran-coupe__522098975f.jpg',
 'images_count': 17,
 'odometer': 125,
 'phone_number': '+38(073) 729 20 00',
 'price_usd': 20999,
 'rid': '35499889',
 'title': 'BMW 4 Series Gran Coupe 2014',
 'url': 'https://auto.ria.com/uk/auto_bmw_4_series_gran_coupe_35499889.html',
 'username': 'Ім’я не вказане' },

  

  

{'car_number': 'AE 7932 TE',
 'car_vin': 'WBA4B3C5xFDxxxx75',
 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/bmw_4-series-gran-coupe__522098975f.jpg',
 'images_count': 17,
 'odometer': 125,
 'phone_number': '+38(073) 729 20 00',
 'price_usd': 20999,
 'rid': '35499889',
 'title': 'BMW 4 Series Gran Coupe 2014',
 'url': 'https://auto.ria.com/uk/auto_bmw_4_series_gran_coupe_35499889.html',
 'username': 'Ім’я не вказане' },
{'car_number': 'AI 1658 PO',
 'car_vin': 'WAUDK78T19A014416',
 'image_url': 'https://cdn3.riastatic.com/photosnew/auto/photo/audi_a5__534363358f.jpg',
 'images_count': 15,
 'odometer': 164,
 'phone_number': '+38(063) 700 21 00',
 'price_usd': 8800,
 'rid': '35956923',
 'title': 'Audi A5 2008',
 'url': 'https://auto.ria.com/uk/auto_audi_a5_35956923.html',
 'username': 'Алексей' },
{'car_number': 'AC 1562 HA',
 'car_vin': 'UU1KSDA3H45502143',
 'image_url': 'https://cdn3.riastatic.com/photosnew/auto/photo/dacia_logan__534363288f.jpg',
 'images_count': 16,
 'odometer': 159,
 'phone_number': '+38(066) 884 11 46',
 'price_usd': 6000,
 'rid': '35956903',
 'title': 'Dacia Logan 2011',
 'url': 'https://auto.ria.com/uk/auto_dacia_logan_35956903.html',
 'username': 'Віталік' },
{'car_number': 'AI 1734 PK',
 'car_vin': 'WBAAL110x0Axxxx43',
 'image_url': 'https://cdn2.riastatic.com/photosnew/auto/photo/bmw_3-series__534358922f.jpg',
 'images_count': 10,
 'odometer': 322,
 'phone_number': '+38(095) 805 38 26',
 'price_usd': 5000,
 'rid': '35956824',
 'title': 'BMW 3 Series 1999',
 'url': 'https://auto.ria.com/uk/auto_bmw_3_series_35956824.html',
 'username': 'Микола Олексадрович' },
{'car_number': None,
 'car_vin': 'JTJBAMCAx02xxxx38',
 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/lexus_rx__533002386f.jpg',
 'images_count': 40,
 'odometer': 50,
 'phone_number': '+38(096) 804 88 88',
 'price_usd': 41500,
 'rid': '35905399',
 'title': 'Lexus RX 2017',
 'url': 'https://auto.ria.com/uk/auto_lexus_rx_35905399.html',
 'username': 'Олексій' },
{'car_number': None,
 'car_vin': 'VF1KZNA0652851485',
 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/renault_megane__534355465f.jpg',
 'images_count': 24,
 'odometer': 256,
 'phone_number': '+38(068) 646 46 57',
 'price_usd': 9750,
 'rid': '35956604',
 'title': 'Renault Megane 2015',
 'url': 'https://auto.ria.com/uk/auto_renault_megane_35956604.html',
 'username': 'Александр' },
{'car_number': None,
 'car_vin': 'VF1JM0U0637006331',
 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/renault_scenic__534363176f.jpg',
 'images_count': 44,
 'odometer': 199,
 'phone_number': '+38(068) 117 07 70',
 'price_usd': 5500,
 'rid': '35956928',
 'title': 'Renault Scenic 2006',
 'url': 'https://auto.ria.com/uk/auto_renault_scenic_35956928.html',
 'username': 'Ім’я не вказане' },
{'car_number': None,
 'car_vin': 'VF1MA000261540919',
 'image_url': 'https://cdn4.riastatic.com/photosnew/auto/photo/renault_master__521183609f.jpg',
 'images_count': 28,
 'odometer': 268,
 'phone_number': '+38(096) 393 45 77',
 'price_usd': 18600,
 'rid': '35464861',
 'title': 'Renault Master 2019',
 'url': 'https://auto.ria.com/uk/auto_renault_master_35464861.html',
 'username': 'Денис' },
{'car_number': 'AX 9569 KK',
 'car_vin': 'XW8ZZZ61ZDG033904',
 'image_url': 'https://cdn2.riastatic.com/photosnew/auto/photo/volkswagen_polo__532917132f.jpg',
 'images_count': 8,
 'odometer': 203,
 'phone_number': '+38(068) 514 00 67',
 'price_usd': 8000,
 'rid': '35902468',
 'title': 'Volkswagen Polo 2012',
 'url': 'https://auto.ria.com/uk/auto_volkswagen_polo_35902468.html',
 'username': 'Максим' },
{'car_number': None,
 'car_vin': 'WP1ZZZ9YZLDA58375',
 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/porsche_cayenne-coupe__485331056f.jpg',
 'images_count': 106,
 'odometer': 39,
 'phone_number': '+38(098) 585 76 67',
 'price_usd': 91900,
 'rid': '34063687',
 'title': 'Porsche Cayenne Coupe 2019',
 'url': 'https://auto.ria.com/uk/auto_porsche_cayenne_coupe_34063687.html',
 'username': 'LUX cars' },]

s = set()
l = []
for d in data:
    s.add(d['rid'])
    l.append(d['rid'])

for rid in s:
    print(rid, '   ', l.count(rid))



# for i, d in enumerate(data):
#     if d['rid'] == '35822515':
#         print(i)

#         35956463