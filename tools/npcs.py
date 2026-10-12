import sys; sys.path.insert(0, '.')
import lpc
lpc.CHARS.update({
    'Mai': ('female', [('body/body.json', 'light', 'body'), ('head/heads/human/heads_human_female_small.json', 'light', 'body'),
                       ('legs/leggings/legs_leggings.json', 'white', 'cloth'), ('feet/shoes/feet_shoes_basic.json', 'white', 'cloth'),
                       ('torso/shirts/longsleeve/torso_clothes_longsleeve2.json', 'white', 'cloth'), ('hair/long/hair_long_straight.json', 'black', 'hair')]),
    'Ông Tư': ('male', [('body/body.json', 'amber', 'body'), ('head/heads/human/heads_human_male_elderly.json', 'amber', 'body'),
                        ('legs/pants/legs_pants.json', 'brown', 'cloth'), ('feet/boots/feet_boots_basic.json', 'black', 'cloth'),
                        ('torso/shirts/longsleeve/torso_clothes_longsleeve2.json', 'green', 'cloth'), ('hair/short/hair_bedhead.json', 'gray', 'hair'),
                        ('hair/mustaches/beards_mustache.json', 'gray', 'hair'), ('headwear/hats/caps/hat_cap_leather.json', None, None)]),
    'Bác sĩ Lan': ('female', [('body/body.json', 'light', 'body'), ('head/heads/human/heads_human_female.json', 'light', 'body'),
                              ('legs/pants/legs_pants.json', 'navy', 'cloth'), ('feet/shoes/feet_shoes_basic.json', 'black', 'cloth'),
                              ('torso/shirts/longsleeve/torso_clothes_longsleeve2.json', 'white', 'cloth'), ('hair/bob/hair_bob.json', 'dark_brown', 'hair'),
                              ('headwear/accessories/glasses/facial_glasses.json', None, None)]),
    'Lính Nhiễm': ('male', [('body/special/body_zombie.json', None, None), ('head/heads/undead/heads_zombie.json', 'zombie', 'body'),
                            ('legs/pants/legs_pants.json', 'forest', 'cloth'), ('torso/shirts/shortsleeve/torso_clothes_tshirt.json', 'forest', 'cloth'),
                            ('headwear/coverings/bandana/hat_bandana.json', 'forest', 'cloth')]),
})
