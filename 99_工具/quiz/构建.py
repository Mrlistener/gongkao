# -*- coding: utf-8 -*-
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
TPL = ROOT / '99_工具' / 'quiz' / '模板.html'

def build(src_json: str, out_html: str) -> str:
    data = json.loads(pathlib.Path(src_json).read_text(encoding='utf-8'))
    tpl = TPL.read_text(encoding='utf-8')
    html = tpl.replace('__TITLE__', data['title'])
    html = html.replace('__SUBTITLE__', data.get('subtitle', ''))
    html = html.replace('__MATERIAL__', data.get('material', ''))
    html = html.replace('<section class="material" id="material">',
                        '<section class="material" id="material" data-set="' + data['title'] + '">')
    html = html.replace('__DATA__', json.dumps(data['questions'], ensure_ascii=False))
    out = pathlib.Path(out_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    return str(out)

if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2]))