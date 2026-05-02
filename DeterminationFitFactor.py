import bisect


def fitfactor(samplefile, somkalibratiefile, wn_min=None, wn_max=None, weights=None):
    cal_wns = sorted(somkalibratiefile.keys())
    residue = 0.0
    for wn, val in samplefile.items():
        if wn_min is not None and wn < wn_min:
            continue
        if wn_max is not None and wn > wn_max:
            continue

        i = bisect.bisect_left(cal_wns, wn)
        if i == 0:
            nearest = cal_wns[0]
        elif i >= len(cal_wns):
            nearest = cal_wns[-1]
        else:
            nearest = cal_wns[i] if abs(cal_wns[i] - wn) <= abs(cal_wns[i - 1] - wn) else cal_wns[i - 1]

        w = 1.0
        if weights:
            for lo, hi, weight in weights:
                if lo <= wn <= hi:
                    w = weight
                    break

        residue += w * abs(val - somkalibratiefile[nearest])
    return residue
