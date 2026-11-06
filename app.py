"""VELORA CINEMA — Premium front end only (Python Tkinter + Pillow).

All 76 catalogue entries are real movies, TV shows or anime. Title-matched
artwork is downloaded on first launch. No fake posters, playback, account
database, server, or authentication are provided.
"""
import os
import math
import queue
import threading
import webbrowser
from pathlib import Path
from urllib.parse import quote_plus
import tkinter as tk
import tkinter.font as tkfont
from PIL import Image, ImageDraw, ImageTk, ImageOps, ImageFilter, ImageEnhance
from catalog import CATALOG as MOVIES, KINDS
from artwork import fetch_all, POSTERS, BACKDROPS

HERE=Path(__file__).resolve().parent
BG='#080A0E'; BAR='#0D1118'; PANEL='#121720'; PANEL2='#18202B'
MUTED='#8D99AA'; SOFT='#B4BBC8'; TEXT='#F7F6F3'; GOLD='#E9C18A'; GOLD_HI='#FFDAA3'; BORDER='#242C36'
FONT='Segoe UI'; DISPLAY='Georgia'
ACCENT={'Movies': GOLD, 'TV Shows': '#76C8E8', 'Anime': '#C8A7FF'}


def fit_image(img, size, center=(.5,.38)):
    return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS, centering=center)


def rgb(hexcolor):
    return tuple(int(hexcolor[i:i+2],16) for i in (1,3,5))


class Velora(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('VELORA CINEMA V5  |  Movies · TV Shows · Anime')
        self.geometry('1536x940')
        self.minsize(1050,710)
        self.configure(bg=BG)
        self.saved=set()
        self.user='Guest'
        self.page='Home'
        self.category='All titles'
        self.genre='All genres'
        self.hero_index=0
        self.photo_cache={}
        self._card_title_font = tkfont.Font(family=FONT, size=13, weight='bold')
        self.work_queue=queue.Queue()
        self.completed=0
        self.loaded=0
        self.fetch_finished=False
        self._resize_after=None
        self.query=tk.StringVar()
        self.query.trace_add('write',self._on_search)
        self._is_login=False
        self._setup()
        self.after(350,self._check_queue)
        threading.Thread(target=self._download_worker,daemon=True).start()

    # ---------- UI scaffolding ----------
    def _setup(self):
        self.header=tk.Canvas(self,height=81,bg=BAR,highlightthickness=0)
        self.header.pack(side='top',fill='x')
        self.body=tk.Frame(self,bg=BG)
        self.body.pack(fill='both',expand=True)
        self.rail=tk.Canvas(self.body,width=93,bg=BAR,highlightthickness=0)
        self.rail.pack(side='left',fill='y')
        self.viewport=tk.Canvas(self.body,bg=BG,highlightthickness=0,yscrollincrement=35)
        # Always-visible vertical scrollbar. Supports track clicks and dragging.
        self.vscroll=tk.Scrollbar(self.body,orient='vertical',command=self.viewport.yview,
                                  bg='#394657',troughcolor='#131922',activebackground=GOLD,
                                  relief='flat',width=15,borderwidth=0,highlightthickness=0)
        self.vscroll.pack(side='right',fill='y')
        self.viewport.configure(yscrollcommand=self.vscroll.set)
        self.viewport.pack(side='left',fill='both',expand=True)
        # Mouse wheel works even when the pointer is over movie images or labels.
        self.bind_all('<MouseWheel>',self._on_wheel,add='+')
        self.bind_all('<Button-4>',lambda e:self._scroll_linux(-3),add='+')
        self.bind_all('<Button-5>',lambda e:self._scroll_linux(3),add='+')
        self.bind_all('<Prior>',lambda e:self._scroll_linux(-13),add='+')
        self.bind_all('<Next>',lambda e:self._scroll_linux(13),add='+')
        self.viewport.bind('<Configure>',self._on_resize)
        self.header.bind('<Configure>',self._on_resize)
        self.rail.bind('<Configure>',self._on_resize)
        self.search_box=tk.Entry(self.header,textvariable=self.query,font=(FONT,12),fg=TEXT,bg=PANEL2,
                                 insertbackground=TEXT,relief='flat',borderwidth=0,highlightthickness=0)
        self.search_window=None
        self.draw_all()

    def _on_resize(self,event=None):
        if self._resize_after is not None:
            self.after_cancel(self._resize_after)
        self._resize_after=self.after(125,self.draw_all)

    def _scroll_linux(self,step):
        if not self._is_login:
            self.viewport.yview_scroll(step,'units')

    def _on_wheel(self,event):
        if not self._is_login:
            step=-int(event.delta/120)*3 if event.delta else 0
            if step:self.viewport.yview_scroll(step,'units')

    def _on_search(self,*_):
        if not hasattr(self,'viewport') or self._is_login:return
        if self.query.get().strip():
            self.page='Browse'; self.category='All titles'; self.genre='All genres'
        self.after_idle(self._search_redraw)

    def _search_redraw(self):
        if not self._is_login and self.winfo_exists():
            self.draw_all();self.viewport.yview_moveto(0)

    def rounded(self,can,x,y,w,h,fill,r=13,outline=None,stroke=1,tags=()):
        # Native vector smooth corners — no hard-edged standard Tk buttons.
        x2,y2=x+w,y+h
        r=min(r,w/2,h/2)
        p=[x+r,y, x2-r,y, x2,y, x2,y+r, x2,y2-r, x2,y2, x2-r,y2,
           x+r,y2, x,y2, x,y2-r, x,y+r, x,y]
        return can.create_polygon(p,smooth=True,splinesteps=18,fill=fill,
                          outline=outline or fill,width=stroke,tags=tags)

    def label(self,can,x,y,text,size=13,color=TEXT,weight='normal',font=FONT,anchor='nw',width=None,tags=()):
        style='bold' if weight=='bold' else 'normal'
        args={'text':text,'fill':color,'font':(font,size,style),'anchor':anchor,'tags':tags}
        if width:args['width']=width
        return can.create_text(x,y,**args)

    def interactive(self,can,tag,callback):
        can.tag_bind(tag,'<Button-1>',lambda e:callback())
        can.tag_bind(tag,'<Enter>',lambda e:can.configure(cursor='hand2'))
        can.tag_bind(tag,'<Leave>',lambda e:can.configure(cursor=''))

    def button(self,can,x,y,w,h,text,action,style='gold',size=12,tag=None):
        if tag is None:tag='tap_'+str(len(can.find_all()))
        base={'gold':GOLD,'dark':PANEL2,'ghost':'#0E131D','white':TEXT}.get(style,GOLD)
        fg=BG if style in ('gold','white') else TEXT
        self.rounded(can,x,y,w,h,base,12,outline=('#343E4B' if style=='ghost' else None),tags=(tag,))
        self.label(can,x+w/2,y+h/2,text,size,fg,'bold',anchor='center',tags=(tag,))
        self.interactive(can,tag,action)

    def photo(self,key,img):
        if key not in self.photo_cache:
            self.photo_cache[key]=ImageTk.PhotoImage(img)
        return self.photo_cache[key]

    def _poster(self,m,w,h):
        path=POSTERS/(m['id']+'.jpg')
        stamp=path.stat().st_mtime if path.exists() else 0
        key=('poster',m['id'],w,h,stamp)
        if key not in self.photo_cache:
            if path.exists():
                try:
                    img=fit_image(Image.open(path).convert('RGB'),(w,h),(.5,.3))
                except Exception:img=self._placeholder(m,w,h)
            else:img=self._placeholder(m,w,h)
            mask=Image.new('L',(w,h));dr=ImageDraw.Draw(mask);dr.rounded_rectangle((0,0,w-1,h-1),radius=12,fill=255)
            img.putalpha(mask)
            self.photo_cache[key]=ImageTk.PhotoImage(img)
        return self.photo_cache[key]

    def _placeholder(self,m,w,h):
        hues=[('#1D2B3F','#475068'),('#32233D','#645372'),('#382A27','#665144'),('#172D38','#436775')]
        c1,c2=hues[sum(map(ord,m['id']))%4]
        im=Image.new('RGB',(w,h));draw=ImageDraw.Draw(im)
        a=rgb(c1);b=rgb(c2)
        for y in range(h):
            t=y/max(1,h-1)
            col=tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
            draw.line((0,y,w,y),fill=col)
        for i in range(5):
            xx=int(w*(.16+i*.2));yy=int(h*(.20+i*.09))
            draw.ellipse((xx-45,yy-45,xx+90,yy+90),outline='#8B8790',width=1)
        # Explicitly marked loading artwork, never misrepresented as a movie poster.
        draw.rectangle((0,int(h*.81),w,h),fill='#121721')
        return im

    def _hero_background(self,m,w,h):
        bd=BACKDROPS/(m['id']+'.jpg')
        pp=POSTERS/(m['id']+'.jpg')
        stamp=(bd.stat().st_mtime if bd.exists() else 0,pp.stat().st_mtime if pp.exists() else 0)
        key=('hero',m['id'],w,h,stamp)
        if key in self.photo_cache:return self.photo_cache[key]
        im=Image.new('RGB',(w,h),'#101720')
        d=ImageDraw.Draw(im)
        # Atmospheric, film-agnostic dark gradient, not a fabricated film still.
        for yy in range(h):
            t=yy/max(1,h)
            d.line((0,yy,w,yy),fill=(int(13+13*t),int(20+10*t),int(30+13*t)))
        glow=Image.new('RGBA',(w,h),(0,0,0,0))
        gd=ImageDraw.Draw(glow)
        gd.ellipse((int(w*.48),-int(h*.75),int(w*1.05),int(h*.95)),fill=(155,100,49,105))
        glow=glow.filter(ImageFilter.GaussianBlur(85))
        im=Image.alpha_composite(im.convert('RGBA'),glow)
        source=bd if bd.exists() else pp if pp.exists() else None
        if source:
            try:
                cover=Image.open(source).convert('RGB')
                # Cinematic real backdrop on right, masked into a dark editorial gradient.
                cover=fit_image(cover,(int(w*.72),h),(.55,.33))
                if source==pp:cover=cover.filter(ImageFilter.GaussianBlur(6))
                cover=ImageEnhance.Brightness(cover).enhance(.78).convert('RGBA')
                alpha=Image.new('L',cover.size);ad=ImageDraw.Draw(alpha)
                for xx in range(cover.width):
                    t=xx/max(1,cover.width)
                    a=0 if t<.12 else int(235*min(1,(t-.12)/.42))
                    ad.line((xx,0,xx,h),fill=a)
                cover.putalpha(alpha)
                im.alpha_composite(cover,(w-cover.width,0))
            except Exception:pass
        ov=Image.new('RGBA',(w,h),(0,0,0,0));od=ImageDraw.Draw(ov)
        for xx in range(w):
            t=xx/max(1,w)
            a=int(170*(1-t)**2)
            od.line((xx,0,xx,h),fill=(6,9,14,a))
        for yy in range(h):
            a=int(120*(yy/max(1,h))**3)
            od.line((0,yy,w,yy),fill=(5,7,11,a))
        im=Image.alpha_composite(im,ov)
        mask=Image.new('L',(w,h),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),radius=24,fill=255)
        im.putalpha(mask)
        self.photo_cache[key]=ImageTk.PhotoImage(im)
        return self.photo_cache[key]

    # ---------- shell ----------
    def draw_all(self):
        if self._is_login:
            self._draw_login();return
        if not hasattr(self,'viewport') or self.viewport.winfo_width()<=1:return
        self._draw_header()
        self._draw_rail()
        self._draw_page()

    def _draw_header(self):
        c=self.header;c.delete('all')
        w=max(1050,c.winfo_width())
        c.create_line(0,80,w,80,fill='#222832')
        self.label(c,124,25,'VELORA',23,TEXT,'bold')
        self.label(c,255,29,'CINEMA',12,GOLD,'bold')
        self.rounded(c,349,26,1,29,'#343943',r=0)
        self.label(c,370,31,'THE ART OF WATCHING',10,MUTED,'bold')
        # Native entry over a rounded custom-drawn search region.
        sw=270 if w<1270 else 332
        sx=w-sw-206
        self.rounded(c,sx,18,sw,46,PANEL2,16)
        self.label(c,sx+16,27,'⌕',23,MUTED,'normal')
        if self.search_window is not None:
            try:c.delete(self.search_window)
            except Exception:pass
        self.search_window=c.create_window(sx+49,40,window=self.search_box,width=sw-67,height=30,anchor='w')
        if not self.query.get():
            self.label(c,sx+50,32,'Search films, shows, anime…',11,MUTED,tags=('search_hint',))
            self.interactive(c,'search_hint',lambda:self.search_box.focus_set())
        self.label(c,w-174,28,'UI DEMO',10,MUTED,'bold')
        status=f'ARTWORK {self.loaded}/{len(MOVIES)}' if self.completed<len(MOVIES) else f'{self.loaded} POSTERS CACHED'
        self.label(c,w-174,48,status,9,GOLD if self.loaded else MUTED)
        self.rounded(c,w-51,20,38,38,GOLD,r=19,tags=('profile',))
        self.label(c,w-32,39,self.user[:1].upper(),12,BG,'bold',anchor='center',tags=('profile',))
        self.interactive(c,'profile',self.show_login)

    def _draw_rail(self):
        c=self.rail;c.delete('all')
        h=max(650,c.winfo_height())
        c.create_line(92,0,92,h,fill='#20252E')
        entries=[('Home','⌂','HOME'),('Movies','▣','MOVIES'),('TV Shows','▤','SHOWS'),
                 ('Anime','✦','ANIME'),('My List','♡','SAVED'),('About','ⓘ','ABOUT')]
        for i,(page,icon,short) in enumerate(entries):
            y=45+i*83
            active=(self.page==page or (page in KINDS and self.category==page and self.page=='Browse'))
            if active:
                self.rounded(c,8,y-14,77,66,'#1B222C',14)
                self.rounded(c,0,y-7,3,51,ACCENT.get(page,GOLD),2)
            tag='rail_'+page.replace(' ','')
            color=ACCENT.get(page,GOLD) if active else MUTED
            self.label(c,46,y,icon,25,color,anchor='center',tags=(tag,))
            self.label(c,46,y+26,short,9,color,'bold',anchor='center',tags=(tag,))
            self.interactive(c,tag,lambda p=page:self.navigate(p))
        self.label(c,46,h-88,'V',24,GOLD,'bold',font=DISPLAY,anchor='center')
        self.label(c,46,h-49,'EST. 2026',8,MUTED,anchor='center')

    def navigate(self,page):
        self.page=page
        self.category=page if page in KINDS else 'All titles'
        self.genre='All genres'
        if page!='Browse' and self.query.get():
            self.query.set('')
        self.draw_all()
        self.viewport.yview_moveto(0)
        if page=='Browse':self.after(60,lambda:self.search_box.focus_set())

    def _draw_page(self):
        c=self.viewport;c.delete('all')
        cw=max(870,c.winfo_width())
        if self.page=='Home': end=self._draw_home(c,cw)
        elif self.page in (*KINDS, 'Browse'):end=self._draw_discover(c,cw)
        elif self.page=='My List':end=self._draw_saved(c,cw)
        else:end=self._draw_about(c,cw)
        c.configure(scrollregion=(0,0,cw,max(end+65,c.winfo_height()+1)))

    def _section_header(self,c,x,y,title,subtitle=None,action=None):
        self.label(c,x,y,title,23,TEXT,'bold')
        if subtitle:self.label(c,x,y+36,subtitle,11,MUTED)
        if action:
            lab,fun=action
            self.label(c,c.winfo_width()-46,y+10,lab,11,GOLD,'bold',anchor='ne',tags=('section_action_'+str(y),))
            self.interactive(c,'section_action_'+str(y),fun)

    def _draw_home(self,c,cw):
        x=43; wide=cw-86
        m=MOVIES[self.hero_index % 5]
        y=30;hh=406
        c.create_image(x,y,image=self._hero_background(m,wide,hh),anchor='nw')
        self.rounded(c,x+34,y+34,144,29,'#323126',13)
        self.label(c,x+106,y+49,"FEATURED MOVIE",10,GOLD_HI,'bold',anchor='center')
        self.label(c,x+38,y+103,m['title'].upper(),41,TEXT,'bold',width=min(640,wide*.56))
        self.label(c,x+41,y+184,f"{m['year']}   •   {m['runtime']}   •   {m['genre']}",12,GOLD_HI,'bold')
        self.label(c,x+41,y+216,m['synopsis'],14,'#E0E3E8',width=min(510,wide*.48))
        self.button(c,x+40,y+313,178,48,'▶  VIEW DETAILS',lambda a=m:self.show_details(a),'gold',12,tag='hero_open')
        self.button(c,x+231,y+313,165,48,'＋  SAVE TITLE',lambda a=m:self.toggle_saved(a),'ghost',12,tag='hero_save')
        self.label(c,x+wide-38,y+hh-36,f'{(self.hero_index%5)+1:02d}  /  05',11,TEXT,'bold',anchor='ne')
        self.button(c,x+wide-155,y+hh-55,36,36,'‹',lambda:self.shift_hero(-1),'dark',16,tag='hero_prev')
        self.button(c,x+wide-112,y+hh-55,36,36,'›',lambda:self.shift_hero(1),'dark',16,tag='hero_next')
        y+=hh+42
        counts={k:len([m for m in MOVIES if m['kind']==k]) for k in KINDS}
        self.label(c,x,y,f"{len(MOVIES)} TITLES     /     {counts['Movies']} MOVIES     /     {counts['TV Shows']} TV SHOWS     /     {counts['Anime']} ANIME",11,GOLD,'bold')
        y+=53
        sections=[('Movies','The big screen, reimagined.','Blockbusters, classics and award-winning stories.'),
                  ('TV Shows','One more episode.','Worlds worth returning to, season after season.'),
                  ('Anime','Entire worlds to discover.','Iconic adventures, powerful heroes and unforgettable animation.')]
        for kind,title,subtitle in sections:
            items=[m for m in MOVIES if m['kind']==kind]
            self._section_header(c,x,y,title,subtitle,(f'ALL {kind.upper()}  →',lambda k=kind:self.navigate(k)))
            y+=87
            y=self._movie_row(c,x,y,cw,items[:6])
            y+=43
        self._footer(c,cw,y+20)
        return y+112

    def shift_hero(self,step):
        self.hero_index=(self.hero_index+step)%5
        self.draw_all()

    def _movie_row(self,c,x,y,cw,movies):
        cols=6 if cw>=1330 else 5 if cw>=1080 else 4
        gap=17
        cardw=int((cw-86-(cols-1)*gap)/cols)
        rows=[movies[i:i+cols] for i in range(0,len(movies),cols)]
        for row in rows:
            for i,m in enumerate(row):self._card(c,x+i*(cardw+gap),y,m,cardw)
            y+=int(cardw*1.43)+92
        return y

    def _card(self,c,x,y,m,w):
        h=int(w*1.43)
        c.create_image(x,y,image=self._poster(m,w,h),anchor='nw',tags=('poster_'+m['id'],))
        self.rounded(c,x+8,y+8,56,24,'#171B23',8,tags=('poster_'+m['id'],))
        self.label(c,x+36,y+20,str(m['year']),9,TEXT,'bold',anchor='center',tags=('poster_'+m['id'],))
        kindlabel={'Movies':'FILM','TV Shows':'SERIES','Anime':'ANIME'}[m['kind']]
        kindcolor=ACCENT[m['kind']]
        self.rounded(c,x+w-78,y+8,70,24,'#111822',8,tags=('poster_'+m['id'],))
        self.label(c,x+w-43,y+20,kindlabel,9,kindcolor,'bold',anchor='center',tags=('poster_'+m['id'],))
        if not (POSTERS/(m['id']+'.jpg')).exists():
            self.label(c,x+w//2,y+h//2-16,'REAL ARTWORK',10,'#D0D5DC','bold',anchor='center',tags=('poster_'+m['id'],))
            self.label(c,x+w//2,y+h//2+8,'Internet needed for poster',9,'#B0B8C3',anchor='center',tags=('poster_'+m['id'],))
        # Crisp overlay bar creates depth without cropping the real poster.
        c.create_rectangle(x,y+h-4,x+w,y+h+2,fill=GOLD if m['id'] in self.saved else BG,outline='')
        name=m['title']
        # Fit titles on one line by actual pixel width, preventing overlap with genre.
        display=name
        if self._card_title_font.measure(display) > w-13:
            while display and self._card_title_font.measure(display+'…') > w-13:
                display=display[:-1]
            display=display.rstrip()+'…'
        self.label(c,x+2,y+h+13,display,13,TEXT,'bold',tags=('poster_'+m['id'],))
        self.label(c,x+2,y+h+46,f"{m['genre']}   •   {m['year']}",10,MUTED,tags=('poster_'+m['id'],))
        heart='♥' if m['id'] in self.saved else '♡'
        self.label(c,x+w-8,y+h+45,heart,19,GOLD if m['id'] in self.saved else MUTED,anchor='ne',tags=('save_'+m['id'],))
        self.interactive(c,'poster_'+m['id'],lambda a=m:self.show_details(a))
        self.interactive(c,'save_'+m['id'],lambda a=m:self.toggle_saved(a))

    def _draw_category_tabs(self,c,cw,y):
        categories=['All titles','Movies','TV Shows','Anime']
        x=43
        for i,kind in enumerate(categories):
            w=151 if kind=='All titles' else 157
            chosen=self.category==kind
            tone=ACCENT.get(kind,GOLD)
            tag='kindtab_'+str(i)
            self.rounded(c,x,y,w,47,tone if chosen else PANEL2,13,tags=(tag,))
            self.label(c,x+w/2,y+24,f'{kind.upper()}  ({len(MOVIES) if kind=="All titles" else sum(m["kind"]==kind for m in MOVIES)})',
                       11,BG if chosen else SOFT,'bold',anchor='center',tags=(tag,))
            self.interactive(c,tag,lambda k=kind:self.change_kind(k))
            x+=w+12
        return y+69

    def change_kind(self,kind):
        self.category=kind
        self.page=kind if kind in KINDS else 'Browse'
        self.genre='All genres'
        self.draw_all()
        self.viewport.yview_moveto(0)

    def _draw_chips(self,c,cw,y):
        relevant=[m for m in MOVIES if self.category=='All titles' or m['kind']==self.category]
        available={g for m in relevant for g in (m['genre'],m['extra'])}
        ordered=['Sci-Fi','Action','Drama','Adventure','Thriller','Animation','Comedy','Romance',
                 'Fantasy','Crime','Mystery','Horror','History','Sports','Workplace','Music']
        genres=['All genres']+[v for v in ordered if v in available]
        x=43
        for i,g in enumerate(genres):
            ww=max(90,29+len(g)*8)
            if x+ww>cw-30:
                y+=52;x=43
            tag='chip_'+str(i)
            color=ACCENT.get(self.category,GOLD)
            self.rounded(c,x,y,ww,37,color if g==self.genre else PANEL2,12,tags=(tag,))
            self.label(c,x+ww/2,y+19,g,11,BG if g==self.genre else SOFT,'bold',anchor='center',tags=(tag,))
            self.interactive(c,tag,lambda a=g:self.change_genre(a))
            x+=ww+10
        return y+46

    def change_genre(self,g):
        self.genre=g
        self.draw_all()
        self.viewport.yview_moveto(0)

    def _draw_discover(self,c,cw):
        x=43;y=42
        title={'All titles':'Explore every story.', 'Movies':'Movies that stay with you.',
               'TV Shows':'Series worth the binge.', 'Anime':'Explore the anime universe.'}[self.category]
        descr={'All titles':'Real movies, television and anime. Three worlds, one cinematic home.',
               'Movies':'Cinema classics, epic adventures, and modern favourites.',
               'TV Shows':'Acclaimed drama, fantasy, thrillers and unforgettable series.',
               'Anime':'Action, fantasy, mystery and animation from Japan.'}[self.category]
        self.label(c,x,y,title,35,TEXT,'bold',font=DISPLAY)
        self.label(c,x,y+59,descr,13,MUTED)
        y=self._draw_category_tabs(c,cw,y+103)+10
        y=self._draw_chips(c,cw,y)+24
        q=self.query.get().strip().lower()
        matches=[m for m in MOVIES if
                 (self.category=='All titles' or self.category==m['kind']) and
                 (self.genre=='All genres' or self.genre in (m['genre'],m['extra'])) and
                 (not q or q in (m['title']+' '+m['genre']+' '+m['extra']+' '+m['director']+' '+m['kind']).lower())]
        self.label(c,x,y,f'{len(matches)} TITLES  •  {self.category.upper()}',11,
                   ACCENT.get(self.category,GOLD),'bold')
        self.label(c,cw-47,y,'SCROLL TO EXPLORE   ↓',10,MUTED,'bold',anchor='ne')
        y+=47
        if not matches:
            self.rounded(c,x,y,cw-86,230,PANEL,18)
            self.label(c,cw/2,y+76,'No matching titles',28,TEXT,'bold',anchor='center')
            self.label(c,cw/2,y+125,'Try another search, category or genre.',12,MUTED,anchor='center')
            return y+280
        cols=5 if cw>=1220 else 4 if cw>=1000 else 3
        gap=19;ww=int((cw-86-(cols-1)*gap)/cols)
        for index,m in enumerate(matches):
            col=index%cols;row=index//cols
            self._card(c,x+col*(ww+gap),y+row*(int(ww*1.43)+101),m,ww)
        bottom=y+math.ceil(len(matches)/cols)*(int(ww*1.43)+101)
        self._footer(c,cw,bottom+25)
        return bottom+100

    def _draw_saved(self,c,cw):
        x=43;y=54
        self.label(c,x,y,'Your watchlist.',37,TEXT,'bold',font=DISPLAY)
        self.label(c,x,y+60,'Movies, series and anime you saved this session. No database or account required.',13,MUTED)
        matches=[m for m in MOVIES if m['id'] in self.saved]
        y+=134
        if not matches:
            self.rounded(c,x,y,cw-86,310,PANEL,22)
            self.label(c,cw/2,y+75,'♡',46,GOLD,anchor='center')
            self.label(c,cw/2,y+153,'Nothing saved yet',26,TEXT,'bold',anchor='center')
            self.label(c,cw/2,y+203,'Explore a film and add it to your list.',13,MUTED,anchor='center')
            self.button(c,cw/2-95,y+240,190,47,'BROWSE ALL TITLES',lambda:self.navigate('Browse'),'gold',11,'empty_explore')
            return y+380
        cols=5 if cw>=1220 else 4
        gap=19;ww=int((cw-86-(cols-1)*gap)/cols)
        for i,m in enumerate(matches):self._card(c,x+(i%cols)*(ww+gap),y+(i//cols)*(int(ww*1.43)+101),m,ww)
        return y+math.ceil(len(matches)/cols)*(int(ww*1.43)+101)+120

    def _draw_about(self,c,cw):
        x=43;y=58;w=cw-86
        self.rounded(c,x,y,w,475,PANEL,22)
        self.label(c,x+43,y+42,'ABOUT THIS PROJECT',11,GOLD,'bold')
        self.label(c,x+43,y+84,'Cinema, beautifully considered.',36,TEXT,'bold',font=DISPLAY)
        message=('VELORA CINEMA is a student front end design project created with Python Tkinter and Pillow. '
                 'It demonstrates a scrollable cinema interface with separate Movie, TV Shows and Anime sections, live search, genre filtering, content details, '
                 'navigation, and a temporary watchlist. It does not provide film playback or real account services.')
        self.label(c,x+44,y+165,message,15,SOFT,width=min(640,w-80))
        self.label(c,x+44,y+284,'REAL FILM, SERIES & ANIME ARTWORK',12,GOLD,'bold')
        self.label(c,x+44,y+319,
                   'Actual film art comes from TMDb or Apple; television from TVmaze, anime from MyAnimeList via Jikan. '
                   'Movie posters belong to the original copyright owners. An internet connection is needed for the first download.',
                   13,MUTED,width=min(655,w-80))
        self.button(c,x+44,y+410,190,46,'EXPLORE CATALOGUE',lambda:self.navigate('Browse'),'gold',11,'about_explore')
        self.button(c,x+248,y+410,183,46,'ARTWORK SOURCE  ↗',lambda:webbrowser.open('https://www.themoviedb.org/'),'ghost',11,'about_source')
        return y+550

    def _footer(self,c,cw,y):
        c.create_line(43,y,cw-43,y,fill=BORDER)
        self.label(c,45,y+22,'VELORA  /  CINEMA',11,MUTED,'bold')
        self.label(c,cw-44,y+23,'MOVIES  /  TV SERIES  /  ANIME    •    FRONT END ONLY',10,MUTED,anchor='ne')

    # ---------- film modal ----------
    def show_details(self,m):
        d=tk.Toplevel(self)
        d.title(m['title']+'  |  Velora Cinema')
        d.configure(bg=BG)
        d.geometry('920x604')
        d.minsize(790,560)
        d.transient(self)
        d.grab_set()
        wrap=tk.Frame(d,bg=BG);wrap.pack(fill='both',expand=True,padx=23,pady=22)
        left=tk.Canvas(wrap,bg=BG,width=340,highlightthickness=0)
        left.pack(side='left',fill='y',padx=(0,34))
        right=tk.Frame(wrap,bg=BG);right.pack(side='left',fill='both',expand=True)
        thumb=self._poster(m,322,480)
        left.create_image(6,2,image=thumb,anchor='nw')
        left.image=thumb
        self._detail_label(right,{'Movies':'FILM DETAILS','TV Shows':'SERIES DETAILS','Anime':'ANIME DETAILS'}[m['kind']],11,GOLD,True,top=12)
        self._detail_label(right,m['title'],29,TEXT,True,top=25,wrap=465)
        self._detail_label(right,f"{m['year']}     •     {m['runtime']}     •     {m['genre']} / {m['extra']}",12,GOLD,True,top=16)
        self._detail_label(right,m['tagline'],14,'#E3E0DB',False,top=25,wrap=440)
        self._detail_label(right,m['synopsis'],13,SOFT,False,top=23,wrap=440)
        self._detail_label(right,'DIRECTED BY' if m['kind']=='Movies' else 'CREATOR / STUDIO',10,MUTED,True,top=24)
        self._detail_label(right,m['director'],13,TEXT,False,top=6,wrap=450)
        btnrow=tk.Frame(right,bg=BG);btnrow.pack(anchor='w',pady=(30,0))
        self._tk_button(btnrow,'VIEW TITLE ONLINE  ↗',lambda:webbrowser.open(m['apple']),True)
        saved=m['id'] in self.saved
        self._tk_button(btnrow,'♥  SAVED' if saved else '＋  MY LIST',lambda:(self.toggle_saved(m),d.destroy()),False)
        self._detail_label(right,'Opens a catalogue or information search. No films or episodes are streamed.',10,MUTED,False,top=20,wrap=425)
        d.bind('<Escape>',lambda e:d.destroy())

    def _detail_label(self,container,value,size,color,bold,top=0,wrap=None):
        lbl=tk.Label(container,text=value,font=(FONT,size,'bold' if bold else 'normal'),fg=color,bg=BG,
                     justify='left',wraplength=wrap or 550,anchor='w')
        lbl.pack(anchor='w',padx=3,pady=(top,0))
        return lbl

    def _tk_button(self,parent,text,cmd,primary):
        tk.Button(parent,text=text,command=cmd,font=(FONT,11,'bold'),fg=BG if primary else TEXT,
                  bg=GOLD if primary else PANEL2,activeforeground=BG if primary else TEXT,
                  activebackground=GOLD_HI if primary else PANEL,relief='flat',bd=0,
                  cursor='hand2',padx=18,pady=14).pack(side='left',padx=(0,12))

    def toggle_saved(self,m):
        if m['id'] in self.saved:self.saved.remove(m['id'])
        else:self.saved.add(m['id'])
        self.draw_all()

    # ---------- Login preview (not authentication) ----------
    def show_login(self):
        self._is_login=True
        self.header.pack_forget()
        self.body.pack_forget()
        if not hasattr(self,'login_canvas'):
            self.login_canvas=tk.Canvas(self,bg=BG,highlightthickness=0)
            self.login_canvas.bind('<Configure>',self._on_resize)
        self.login_canvas.pack(fill='both',expand=True)
        self._draw_login()

    def _draw_login(self):
        if not self._is_login:return
        c=self.login_canvas;c.delete('all')
        w=max(1040,c.winfo_width());h=max(700,c.winfo_height())
        panelw=430
        panelx=w-panelw-75
        # Editorial left hand side; authentic artwork in an offset collage.
        self.label(c,70,53,'V',38,GOLD,'bold',font=DISPLAY)
        self.label(c,117,61,'VELORA  /  CINEMA',17,TEXT,'bold')
        self.label(c,80,171,'EVERY GREAT',40,TEXT,'bold',font=DISPLAY)
        self.label(c,80,224,'STORY STARTS',40,TEXT,'bold',font=DISPLAY)
        self.label(c,80,277,'SOMEWHERE.',40,GOLD,'bold',font=DISPLAY)
        self.label(c,84,353,'Films. Television. Anime. One beautiful place.\nCurated for those who love a great story.',14,SOFT,width=530)
        iw=min(176,max(123,(panelx-130)//3))
        for j,m in enumerate([MOVIES[0],MOVIES[1],MOVIES[2]]):
            py=int(h*.54)+ (j%2)*35
            px=82+j*(iw+13)
            c.create_image(px,py,image=self._poster(m,iw,int(iw*1.42)),anchor='nw')
        self.label(c,84,h-49,'DESIGNED FOR THE LOVE OF FILM   •   FRONT END EXPERIENCE',10,MUTED,'bold')
        self.rounded(c,panelx,round(h*.5-276),panelw,552,PANEL,23,outline='#2F3842')
        top=round(h*.5-276)
        self.label(c,panelx+36,top+36,'WELCOME TO VELORA',11,GOLD,'bold')
        self.label(c,panelx+36,top+80,'Your seat is ready.',31,TEXT,'bold',font=DISPLAY)
        self.label(c,panelx+36,top+143,'Enter any name to explore the demo.',12,MUTED)
        self.label(c,panelx+36,top+201,'YOUR NAME',11,SOFT,'bold')
        self.rounded(c,panelx+35,top+233,panelw-70,54,PANEL2,11)
        if not hasattr(self,'login_name'):
            self.login_name=tk.Entry(self.login_canvas,font=(FONT,14),fg=TEXT,bg=PANEL2,insertbackground=TEXT,
                                     relief='flat',highlightthickness=0)
        c.create_window(panelx+55,top+260,window=self.login_name,width=panelw-111,height=35,anchor='w')
        self.button(c,panelx+35,top+314,panelw-70,53,'ENTER THE CINEMA   →',self.enter_demo,'gold',12,'enter_cinema')
        self.label(c,panelx+panelw/2,top+394,'OR',11,MUTED,'bold',anchor='center')
        self.button(c,panelx+35,top+422,panelw-70,47,'CONTINUE AS GUEST',self.enter_guest,'ghost',11,'enter_guest')
        self.label(c,panelx+panelw/2,top+511,'Front end only  ·  No account or server required',10,MUTED,anchor='center')

    def enter_demo(self):
        self.user=(self.login_name.get().strip()[:18] if hasattr(self,'login_name') else '') or 'Guest'
        self._exit_login()

    def enter_guest(self):
        self.user='Guest';self._exit_login()

    def _exit_login(self):
        self._is_login=False
        self.login_canvas.pack_forget()
        self.header.pack(side='top',fill='x')
        self.body.pack(fill='both',expand=True)
        self.page='Home'
        self.draw_all()
        self.viewport.yview_moveto(0)

    # ---------- Artwork download worker ----------
    def _download_worker(self):
        def update(m,p,b,i,total):self.work_queue.put((m['id'],p,b,i,total))
        try:fetch_all(update)
        except Exception:pass
        finally:self.work_queue.put(('DONE',False,False,0,0))

    def _check_queue(self):
        redraw=False
        changed=set()
        try:
            while True:
                movie_id,p,b,i,total=self.work_queue.get_nowait()
                if movie_id=='DONE':self.fetch_finished=True;redraw=True;continue
                self.completed+=1
                if p:self.loaded+=1
                if p or b:
                    redraw=True
                    changed.add(movie_id)
        except queue.Empty:pass
        if redraw:
            # Preserve cached artwork for all other titles during background downloads.
            for key in list(self.photo_cache):
                if isinstance(key,tuple) and len(key)>1 and key[0] in ('poster','hero') and key[1] in changed:
                    del self.photo_cache[key]
            self.draw_all()
        if not self.fetch_finished:self.after(550,self._check_queue)


if __name__=='__main__':
    app=Velora()
    app.mainloop()
