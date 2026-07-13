from iztro_py import astro

c = astro.by_solar('1991-8-15', 1, '男')

soul = c.get_soul_palace()
body = c.get_body_palace()

print("命宫 index:", soul.index)
print("命宫 name:", str(soul))
print("命宫 translate_name:", soul.translate_name() if hasattr(soul, 'translate_name') else 'N/A')
print("命宫 earthly_branch:", soul.earthly_branch)
print("命宫 heavenly_stem:", soul.heavenly_stem if hasattr(soul, 'heavenly_stem') else 'N/A')
print("命宫 major_stars:", [str(s) for s in soul.major_stars])
print("命宫 minor_stars:", [str(s) for s in soul.minor_stars])

star = soul.major_stars[0]
print("first star:", star)
print("star translate_name:", star.translate_name() if hasattr(star, 'translate_name') else 'N/A')
print("star mutagen:", star.mutagen if hasattr(star, 'mutagen') else 'N/A')

print("\ndecadal:", soul.decadal)
if soul.decadal:
    print("  range:", soul.decadal.range)
    print("  heavenly_stem:", soul.decadal.heavenly_stem if hasattr(soul.decadal, 'heavenly_stem') else 'N/A')
    print("  earthly_branch:", soul.decadal.earthly_branch if hasattr(soul.decadal, 'earthly_branch') else 'N/A')

print("\nempty_palaces:", c.empty_palaces() if callable(getattr(c, 'empty_palaces', None)) else 'N/A')
print("lunar_date:", c.lunar_date if hasattr(c, 'lunar_date') else 'N/A')
print("chinese_date:", c.chinese_date if hasattr(c, 'chinese_date') else 'N/A')
print("five_elements_class:", c.five_elements_class)
