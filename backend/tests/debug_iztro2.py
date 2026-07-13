from iztro_py import astro

c = astro.by_solar('1991-8-15', 1, '男')

p = c.palaces[0]
print("palace 0 name:", p.translate_name())
print("palace 0 major_stars:", len(p.major_stars))
print("palace 0 minor_stars:", len(p.minor_stars))
print("has adjective_stars:", hasattr(p, 'adjective_stars'))
if hasattr(p, 'adjective_stars'):
    print("adjective_stars count:", len(p.adjective_stars))
    if p.adjective_stars:
        print("first adj star:", p.adjective_stars[0])
        print("first adj star translate:", p.adjective_stars[0].translate_name() if hasattr(p.adjective_stars[0], 'translate_name') else 'N/A')

print("\nhas decadal:", p.decadal is not None if hasattr(p, 'decadal') else 'N/A')
if p.decadal:
    print("decadal type:", type(p.decadal))
    print("decadal dir:", [x for x in dir(p.decadal) if not x.startswith('_')])

print("\nstar mutagen check:")
for palace in c.palaces:
    for s in list(palace.major_stars) + list(palace.minor_stars):
        if hasattr(s, 'mutagen') and s.mutagen:
            print(f"  {s.translate_name()}: {s.mutagen}")

print("\nempty_palaces callable?", callable(getattr(c, 'empty_palaces', None)))
if callable(getattr(c, 'empty_palaces', None)):
    eps = c.empty_palaces()
    print("empty palaces count:", len(eps))
    for ep in eps:
        print("  ", ep.earthly_branch if hasattr(ep, 'earthly_branch') else str(ep))

print("\nlunar_date:", hasattr(c, 'lunar_date'), c.lunar_date if hasattr(c, 'lunar_date') else 'N/A')
print("chinese_date:", hasattr(c, 'chinese_date'), c.chinese_date if hasattr(c, 'chinese_date') else 'N/A')
