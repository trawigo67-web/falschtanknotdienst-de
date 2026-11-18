import sys,subprocess,os
from playwright.sync_api import sync_playwright
q,part,parts,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
v='fmt=v' in q
tmp=out.replace('.mp4','.tmp.mp4')
with sync_playwright() as p:
    br=p.chromium.launch(); pg=br.new_page(viewport={'width':1080 if v else 1920,'height':1920 if v else 1080})
    pg.goto('file:///home/claude/video/anim.html?'+q); pg.evaluate("document.fonts.load(\"800 40px SSC\").then(()=>document.fonts.ready).then(()=>1)")
    n=round(pg.evaluate("DUR")*30); a=n*part//parts; b=n*(part+1)//parts
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-c:v','mjpeg','-framerate','30','-i','-','-c:v','libx264','-crf','18','-preset','veryfast','-pix_fmt','yuv420p','-r','30',tmp],stdin=subprocess.PIPE)
    for i in range(a,b):
        pg.evaluate(f"setTime({i/30})"); ff.stdin.write(pg.screenshot(type='jpeg',quality=92))
    br.close()
ff.stdin.close(); rc=ff.wait()
if rc==0: os.rename(tmp,out)
sys.exit(rc)
