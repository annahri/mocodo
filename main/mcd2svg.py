#!/usr/bin/env python
# encoding: utf-8

from main.mcd import *
from main.common import *
import re

def main(params):
	common = Common(params)
	style = common.loadStyle()
	mcd = Mcd(common.loadInputFile(),params)
	mcd.calculateSize(style)
	result = []
	result.append("#!/usr/bin/env python")
	result.append("# encoding: utf-8")
	result.append("# %s\n" % common.timeStamp())
	result.append("import time, codecs\n")
	result.extend(common.processGeometry(mcd,style))
	result.append("cardMaxWidth = %(cardMaxWidth)s\ncardMaxHeight = %(cardMaxHeight)s\ncardMargin = %(cardMargin)s\narrowWidth = %(arrowWidth)s\narrowHalfHeight = %(arrowHalfHeight)s\narrowAxis = %(arrowAxis)s" % style)
	result.append(open("main/goodies.py").read())
	result.append(open("main/svggoodies.py").read())
	result.append("""\nlines = '<?xml version="1.0" standalone="no"?>\\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\\n"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'""")
	result.append("""lines += '\\n\\n<svg width="%s" height="%s" viewBox="0 0 %s %s"\\nxmlns="http://www.w3.org/2000/svg"\\nxmlns:link="http://www.w3.org/1999/xlink">' % (width,height,width,height)""")
	result.append(_("""lines += u'\\n\\n<desc>Generated by Mocodo %s on %s</desc>'""") % (version,"%s") + """ % time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())""")
	result.append("""lines += '\\n\\n<rect x="0" y="0" width="%s" height="%s" fill="%s" stroke="none" stroke-width="0"/>' % (width,height,colors['backgroundColor'] if colors['backgroundColor'] else "none")""")
	commands = {
		"roundRect":      """<rect x="%(x)s" y="%(y)s" width="%(w)s" height="%(h)s" fill="%(color)s" rx="%(radius)s" stroke="%(strokeColor)s" stroke-width="%(strokeDepth)s"/>""",
		"lowerRoundRect": """<path d="%(path)s" fill="%(color)s" stroke="%(strokeColor)s" stroke-width="%(strokeDepth)s"/>""",
		"upperRoundRect": """<path d="%(path)s" fill="%(color)s" stroke="%(strokeColor)s" stroke-width="%(strokeDepth)s"/>""",
		"lineArrow":      """<path d="%(path)s" fill="%(strokeColor)s" stroke-width="0"/>""",
		"curveArrow":     """<path d="%(path)s" fill="%(strokeColor)s" stroke-width="0"/>""",
		"line":           """<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(strokeColor)s" stroke-width="%(strokeDepth)s"/>""",
		"rect":           """<rect x="%(x)s" y="%(y)s" width="%(w)s" height="%(h)s" fill="%(color)s" stroke="%(strokeColor)s" stroke-width="%(strokeDepth)s"/>""",
		"circle":         """<circle cx="%(cx)s" cy="%(cy)s" r="%(r)s" stroke="%(strokeColor)s" stroke-width="%(strokeDepth)s" fill="%(color)s"/>""",
		"text":           """<text x="%(x)s" y="%(y)s" fill="%(textColor)s" font-family="%(family)s" font-size="%(size)s">%(text)s</text>""",
		"card":           """<text x="%(tx)s" y="%(ty)s" fill="%(textColor)s" font-family="%(family)s" font-size="%(size)s">%(text)s</text>""",
		"dashLine":       """<line x1="%(x0)s" y1="%(y)s" x2="%(x1)s" y2="%(y)s" style="fill:none;stroke:%(strokeColor)s;stroke-width:%(strokeDepth)s;stroke-dasharray:%(dashWidth)s;"/>""",
		"circle":         """<circle cx="%(cx)s" cy="%(cy)s" r="%(r)s" stroke="%(strokeColor)s" stroke-width="%(strokeDepth)s" fill="%(color)s"/>""",
		"curve":          """<path d="M%(x0)s %(y0)s C %(x1)s %(y1)s %(x2)s %(y2)s %(x3)s %(y3)s" fill="none" stroke="%(strokeColor)s" stroke-width="%(strokeDepth)s"/>""",
		"begin":          """<g id="%(id)s">""",
		"end":            """</g>""",
	}
	legs = dict((leg.identifier(),leg.value()) for row in mcd.ordering for box in row for leg in box.legs)
	others = {}
	tabs = 0
	rex = re.compile(r"(?<=%\().+?(?=\)s)")
	for d in mcd.description():
		if type(d) is dict:
			if d["key"] == "env":
				result.append("(%s) = (%s)" % (",".join(zip(*d["env"])[0]),",".join(zip(*d["env"])[1])))
			else:
				if d["key"] == "card":
					result.append('(tx,ty) = cardPos(%(ex)s,%(ey)s,%(ew)s,%(eh)s,%(ax)s,%(ay)s,k[u"%(legIdentifier)s"])' % d)
				elif d["key"] == "upperRoundRect":
					result.append('path = upperRoundRect(%(x)s,%(y)s,%(w)s,%(h)s,%(radius)s)' % d)
				elif d["key"] == "lowerRoundRect":
					result.append('path = lowerRoundRect(%(x)s,%(y)s,%(w)s,%(h)s,%(radius)s)' % d)
				elif d["key"] == "lineArrow":
					result.append('path = lineArrow(%(x0)s,%(y0)s,%(x1)s,%(y1)s,t[u"%(legIdentifier)s"])' % d)
				elif d["key"] == "curveArrow":
					result.append('path = curveArrow(%(x0)s,%(y0)s,%(x1)s,%(y1)s,%(x2)s,%(y2)s,%(x3)s,%(y3)s,t[u"%(legIdentifier)s"])' % d)
				elif d["key"] in ("color","strokeColor"):
					others[d["key"]] = "colors['%s']" % d[d["key"]]
				elif d["key"] == "strokeDepth":
					others["strokeDepth"] = d["strokeDepth"]
				tabs = tabs - (1 if d["key"] == "end" else 0)
				if d["key"] in commands:
					d.update(others)
					for k in d:
						if type(d[k]) is str and d[k].endswith("Color"):
							d[k] = "colors['%s']" % d[k]
					line = commands[d["key"]]
					subDict = dict((key,"%("+key+")s") for key in rex.findall(line))
					for k in subDict:
						if k in d and type(d[k]) is not str:
							subDict[k] = d[k]
					line = line % subDict
					subDict = "{%s}" % ", ".join("'%s': %s" % (k,(d[k] if k in d else k)) for k in rex.findall(line))
					result.append("lines += u\"\"\"\\n%s\"\"\"" % ("\t"*tabs+line) + " % " + str(subDict))
				tabs = tabs + (1 if d["key"] == "begin" else 0)
		else:
			result.append("\nlines += u\"\"\"\\n\\n<!-- %s -->\"\"\"" % d)
	result.append("""lines += u'\\n</svg>'""")
	result.append("""\nimport codecs\ncodecs.open("%(root)s.svg","w","utf8").write(lines)""" % params)
	result.append(_("""safePrint(u'Output file "%(root)s.svg" successfully generated.')""") % params)
	common.dumpOutputFile("\n".join(result))
	common.dumpMldFiles(mcd)
	