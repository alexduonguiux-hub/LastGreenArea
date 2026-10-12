"""Weapon database v2 — re-drawn in the style of the user's reference sheet: dark violet-black steel,
tan / rust-red furniture, suppressors, scopes, bipods, ammo boxes, plus launcher and grenades.
Original pixel maps (muzzle points left)."""
import weapons_db
from weapons_db import Image

PAL = {'d': (38, 34, 44), 'm': (58, 52, 68), 'l': (88, 80, 100), 'w': (128, 118, 142),
       't': (110, 92, 68), 'T': (152, 130, 96), 'Y': (190, 168, 128),
       'r': (118, 44, 32), 'R': (168, 72, 52), 'Q': (204, 108, 80),
       'g': (84, 98, 42), 'G': (126, 142, 66), 'y': (236, 176, 60), 'b': (150, 110, 60), 'x': (210, 60, 50)}

W = {
 'pistol': dict(name='Súng ngắn', cls='pistol', grip=(11, 5), muzzle=(0, 2), dmg=2, rng=2, noise=3, rate=3, map=[
  '..wwwwwwwwwww...',
  '.lmmmmmmmmmmmd..',
  'lmmmmmmmmdmdmd..',
  '..dddddddmmmmd..',
  '......d.d.dmmd..',
  '.......dd.dmmmd.',
  '...........dmmd.',
  '...........dddd.']),
 'revolver': dict(name='Súng lục ổ quay', cls='pistol', grip=(15, 5), muzzle=(0, 1), dmg=3, rng=2, noise=4, rate=2, map=[
  '..............ww..',
  'lllllllllwwwwmmw..',
  'mmmmmmmmmlmlmlmd..',
  '.dd......mlmlmmd..',
  '..........dd.dRR..',
  '...........d..RQr.',
  '..............RRr.',
  '...............RRr']),
 'silenced': dict(name='Súng giảm thanh', cls='pistol', grip=(16, 4), muzzle=(0, 1), dmg=2, rng=2, noise=1, rate=3, map=[
  '........wwwwwwww....',
  'lmlmlmlmlmmmmmmmml..',
  'dddddddd.dddddmmmd..',
  '.............d.dmm..',
  '..............d.dmm.',
  '................dmmd',
  '.................ddd']),
 'mac': dict(name='Tiểu liên giảm thanh', cls='smg', grip=(15, 4), muzzle=(0, 2), dmg=1, rng=2, noise=2, rate=5, map=[
  '..........wwwwww...d',
  '..........mmmmmmm.d.',
  'lmlmlmlmlmmmmmmmmdd.',
  'dddddddd..dddmmd....',
  '.............mm.....',
  '.............Rm.....',
  '.............RR.....']),
 'uzi': dict(name='Tiểu liên nhỏ', cls='smg', grip=(7, 4), muzzle=(0, 2), dmg=1, rng=2, noise=4, rate=5, map=[
  '...m......m..',
  'wwwwwwwwwwwww',
  'mmmmmmmmmmmmd',
  'ddddddmmmdddd',
  '......mm.....',
  '......lm.....',
  '......mm.....',
  '......dd.....']),
 'ar_tan': dict(name='Súng trường (cát)', cls='rifle', grip=(20, 6), muzzle=(0, 3), dmg=3, rng=4, noise=4, rate=4, map=[
  '................ww..............',
  '...............mmmm.............',
  'dmdmdmd.TTTTTTTTmmmmmmmmmm..mmmm',
  'mmmmmmmmTtTtTtTtmmmmmmmmmmmmm..m',
  'dmdmdmd.TTTTTTTTmmmmmmddmmm.mm.m',
  '..........T......mm.mm...mmmmmmm',
  '..........T.....mm..mm.....tttt.',
  '...............mm...mm..........',
  '..............dd.....d..........']),
 'ar_scope': dict(name='Súng trường ống ngắm', cls='rifle', grip=(20, 7), muzzle=(0, 4), dmg=3, rng=5, noise=4, rate=4, map=[
  '.............TTTTTTTT...........',
  '.............tYYYYYYt...........',
  '...............mmmm.............',
  'dmdmdmd.TTTTTTTTmmmmmmmmmm..mmmm',
  'mmmmmmmmTtTtTtTtmmmmmmmmmmmmm..m',
  'dmdmdmd.TTTTTTTTmmmmmmddmmm.mm.m',
  '..........T......mm.mm...mmmmmmm',
  '..........T.....mm..mm.....tttt.',
  '...............mm...mm..........',
  '..............dd.....d..........']),
 'ar_red': dict(name='Súng trường (đỏ)', cls='rifle', grip=(20, 6), muzzle=(0, 3), dmg=3, rng=4, noise=5, rate=4, map=[
  '................ww..............',
  '...............mmmm.............',
  'dmdmdmd.RRRRRRRRmmmmmmmmmm..mmmm',
  'mmmmmmmmRrRrRrRrmmmmmmmmmmmmm..m',
  'dmdmdmd.RRRRRRRRmmmmmmddmmm.mm.m',
  '..........R......mm.mm...mmmmmmm',
  '..........R.....mm..mm.....rrrr.',
  '...............mm...mm..........',
  '..............dd.....d..........']),
 'lmg': dict(name='Trung liên', cls='rifle', grip=(22, 5), muzzle=(0, 3), dmg=4, rng=4, noise=5, rate=5, map=[
  '..........wwwwwwwwww..............',
  '.........mmmmmmmmmmmm.............',
  'lmlmlmmmmmmmmmmmmmmmmmmmmmmmm..mmm',
  'mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm.m',
  '......d.....mmyyymmmdmmdmmmmmmmmmm',
  '.....d.d....myyyymm..mm...mmmmm...',
  '....d...d...mmmmmm...mm...........',
  '.............dddd.................']),
 'sniper_tan': dict(name='Súng bắn tỉa (cát)', cls='sniper', grip=(25, 6), muzzle=(0, 4), dmg=5, rng=5, noise=5, rate=1, map=[
  '..............TTTTTTTTTT............',
  '..............tYYYYYYYYt............',
  '................m......m............',
  'dmdmdmdmlllllllllllTTTTTTTTTTTTTTTTT',
  'mmmmmmmmmmmmmmmmmmmtTtTtTtTTttTTTTTT',
  'dmdmdmdm...........TTTTmmd..tT..TTT.',
  '..........d..........mm.mm..T....TT.',
  '.........d.d..........m..m...TTTTT..']),
 'sniper_black': dict(name='Súng bắn tỉa nòng dài', cls='sniper', grip=(25, 5), muzzle=(0, 3), dmg=5, rng=5, noise=4, rate=1, map=[
  '.................wwwwwwwww........',
  '.................mmmmmmmmm........',
  '..................m.....m.........',
  'lmlmmmmmmmmmmmmmmmmmmmmmmmmmmmmm..',
  'dddddddddddmmmmmmmmmmmmmmmmmmmmmmm',
  '................d..mmd.ddm..mm.mmm',
  '...............d.d.md..dm...m..mmm']),
 'shotgun': dict(name='Súng săn bơm', cls='shotgun', grip=(19, 3), muzzle=(0, 1), dmg=4, rng=1, noise=5, rate=1, map=[
  '.mmmmmmmmmmmmmmmmmmm........',
  'lwwwwwwwwwwwwwwwwmmmmm......',
  'ddddTTTTTTTddddddmmmmmmmT...',
  '....ttttttt.........ddmmTTTT',
  '......................TTTTTT',
  '.......................TT.TT']),
 'sawed': dict(name='Súng săn cưa nòng', cls='shotgun', grip=(10, 3), muzzle=(0, 1), dmg=4, rng=1, noise=5, rate=1, map=[
  '.mmmmmmmmmmmm....',
  'lwwwwwwwwwwmmmm..',
  'ddRRRRRddddmmmmQ.',
  '..rrrrr.....dRRRR',
  '............RRR..',
  '...........RR....']),
 'rpg': dict(name='Súng phóng lựu', cls='launcher', grip=(18, 5), muzzle=(0, 2), dmg=5, rng=4, noise=5, rate=1, map=[
  '..GG..........................',
  '.GGGG.........................',
  'gGGGGGRRRRRRRRRRRRRRRRRRRRRRRR',
  'gGGGGGRrrrrrrrrrrrmmmrrrrrrrrr',
  '.gggg.........mmm.mmd.........',
  '..gg...........md..md.........',
  '...............md.............']),
 'grenade': dict(name='Lựu đạn', cls='throw', grip=(3, 4), muzzle=(3, 0), dmg=5, rng=3, noise=5, rate=1, map=[
  '..lw..',
  '.mmmd.',
  'gGGGgg',
  'GgGgGg',
  'gGGGgg',
  '.gggg.']),
 'smoke': dict(name='Lựu khói', cls='throw', grip=(3, 4), muzzle=(3, 0), dmg=0, rng=3, noise=2, rate=1, map=[
  '..lw.',
  '.mmmd',
  'lwwwm',
  'mxxxd',
  'mmmmd',
  'lwwwm',
  'mmmmd']),
}

def install():
    """Swap the live database to v2 so every pose builder and the exporter use the new sprites."""
    weapons_db.PAL.update(PAL); weapons_db.W.clear(); weapons_db.W.update(W)
    weapons_db.POSE.update({'launcher': 'shoulder', 'throw': 'throw', 'melee_short': 'blade_short', 'melee_long': 'blade_long'})

W.update({
 'knife': dict(name='Dao ngắn', cls='melee_short', grip=(9, 1), muzzle=(0, 1), dmg=2, rng=1, noise=1, rate=4, map=[
  '.wwwww......',
  'wcccccmdbbbb',
  '.dddddm.bbb.']),
 'machete': dict(name='Dao rựa', cls='melee_long', grip=(17, 2), muzzle=(0, 2), dmg=4, rng=1, noise=2, rate=2, map=[
  '..wwwwwwwwwwwww.......',
  '.wcccccccccccccw......',
  'wcccccccccccccccmbbbbb',
  '.ddcccccccccccdm.bbbbb',
  '...dddddddddddd.......']),
})

# ---- v3: SMG line-up re-drawn from the user's new reference sheet (replaces 'mac' and 'uzi')
SMG3 = {
 'smg_fold': ('Tiểu liên báng gập', (12, 2), (0, 1), (2, 2, 3, 5), [
  'mmmmmmmmmmmmmmmmmm.ddddd',
  'lwwwwwwwwwwmmmmmmmmd...d',
  '.dd....dmmmmmdmmmd.dddd.',
  '.........mm...mmd.......',
  '.........mm....md.......',
  '.........lm.............',
  '.........mm.............',
  '.........dd.............']),
 'smg_scorpion': ('Tiểu liên bọ cạp', (14, 3), (0, 1), (2, 2, 3, 5), [
  '..d.....mmmmmmm...',
  'mmmmmmmmmlllmmmmd.',
  '.ddmmmmmmmmmmmmdd.',
  '....dm....mmd..dmd',
  '..........lm....dd',
  '..........mm......']),
 'smg_box': ('Tiểu liên hộp', (7, 4), (0, 1), (2, 2, 4, 5), [
  '..dddd..........',
  'mmmmmmmmmmmmmd.d',
  'lwwwwwwwwwwwmdd.',
  '.dddddmmmmmmmd..',
  '......mm.m......',
  '......lm........',
  '......mm........',
  '......lm........',
  '......dd........']),
 'smg_pdw': ('Tiểu liên PDW', (8, 3), (0, 1), (2, 3, 3, 5), [
  '......d.d.d.d.......',
  'lmlmmmmmmmmmmmmmm..d',
  '.mmmmmmmmmmmmmmmmmdd',
  '.ddddd.mmd...mmd..d.',
  '.......mm.....md....',
  '......mm............',
  '.....mm.............',
  '.....dd.............']),
 'smg_skeleton': ('Tiểu liên khung rỗng', (19, 3), (0, 1), (2, 3, 3, 4), [
  '.....................mmmmmm.',
  'mmmmmmlwlwlwlwlwmmmmmmmm.mmm',
  '.dddddddddddddddmmmmmmmm.m.m',
  '...............m..mmd.dmmmmm',
  '...............d...md.......']),
 'smg_p90': ('Tiểu liên đạn ngang', (17, 4), (0, 2), (2, 3, 3, 5), [
  '..............oooooooo..',
  '.ooooooooooooooyoooooooo',
  'mooooooyyyyyyooooooooooo',
  '.ooooooooooooooooooooooo',
  '.oooddddooo....oddddooo.',
  '..oo.dd.oo......dd..oo..']),
 'smg_bullpup': ('Tiểu liên bullpup', (14, 4), (0, 2), (3, 4, 3, 5), [
  '.........dmmmmmmmmmm......',
  '.mmmmmmmmmmmmmmmmmmmmmmmm.',
  'lmlwwwwwwwwwwwwwwwwwmmmmmm',
  '.mmmmmmmmmmmmmmmmmmmmmmmmm',
  '.....mmmd...dmmmmmmmmmmmmm',
  '......dd.....mmd.....dmmd.',
  '...............d....dmmd..']),
 'smg_olive': ('Tiểu liên giảm thanh ô liu', (14, 2), (0, 1), (2, 1, 4, 5), [
  'lolololo....mmmmmm........',
  'oooooooommmmmmmmmmmmmm..mm',
  'dddddddd.dddmmmmdd.d...m.m',
  '............ommd.....mmmmm',
  '............ood...........',
  '............ood...........']),
 'smg_wood': ('Tiểu liên báng gỗ', (15, 3), (0, 1), (2, 2, 4, 4), [
  'TtTtTtT.......................',
  'TTTTTTTTTmmmmmmmmmmm..........',
  'tttttttttmmmmmmmmmmmmBBBBBBBBB',
  '.........dmmd..mmd..bbbbbbbbbb',
  '..........mm....md............',
  '..........mm..................',
  '..........dd..................']),
 'smg_vector': ('Tiểu liên khung cát', (9, 3), (0, 1), (2, 3, 3, 5), [
  '......TTTTTTTTT.........',
  'lmlmmmmmmmmmmmmmmT...T..',
  '.ddddmmmmmmmmmmmmTTTTT..',
  '.......TTmmmd..TT.......',
  '......TT.mm.....TT......',
  '.....TT..mm.............',
  '.........TT.............',
  '.........tt.............']),
 'smg_square': ('Tiểu liên vuông', (14, 3), (0, 1), (2, 2, 3, 4), [
  'mmmmmmmmmmmmmmmmmmm...',
  'lwwwwwwwwwwwwmmmmmmmmm',
  '.ddddddddmmmmmmmmmmmmm',
  '.........mm..mmd..dmmm',
  '.........mm...md......',
  '.........lm...........',
  '.........dd...........']),
}

NEUTRAL = {'a': (32, 34, 38), 's': (66, 70, 76), 'e': (108, 114, 120), 'h': (164, 170, 176)}
def install_v3():
    install(); weapons_db.PAL.update(NEUTRAL)
    for k in ('mac', 'uzi'): weapons_db.W.pop(k, None)
    order = list(weapons_db.W.items()); weapons_db.W.clear()
    for k, v in order:
        weapons_db.W[k] = v
        if k == 'silenced':
            for sid, (name, grip, muzzle, st, mp) in SMG3.items():
                weapons_db.W[sid] = dict(name=name, cls='smg', grip=grip, muzzle=muzzle, dmg=st[0], rng=st[1], noise=st[2], rate=st[3], map=[r.translate(str.maketrans('dmlw', 'aseh')) for r in mp])
