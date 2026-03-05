from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Sum, F, Case, When, IntegerField
from django.http import Http404
from .models import *

def bas_sahypa(request):
    # Esasy statistika
    umumy_oyuncu = Oyuncu.objects.filter(aktiv=True).count()
    yenis_gazanan = YarysGatnashyk.objects.filter(netije='yenis').values('oyuncu').distinct().count()
    yarys_sany = Yarys.objects.count()
    fakultet_sany = Fakultet.objects.count()
    sport_sany = SportGornushi.objects.count()
    
    # Soňky ýaryşlar (gutaryan_sene ýok bolsa, baslanjak_sene ulanylyar)
    sonky_yaryslar = Yarys.objects.filter(status='tamamlanyldy')
    # gutaryan_sene bar bolsa ulanylyk, ýok bolsa baslanjak_sene
    try:
        sonky_yaryslar = sonky_yaryslar.order_by('-gutaryan_sene')[:5]
    except:
        sonky_yaryslar = sonky_yaryslar.order_by('-baslanjak_sene')[:5]
    
    # Iň gowy oýunçylar
    oyuncular = Oyuncu.objects.filter(aktiv=True).annotate(
        yenis_sany=Count('yarysgatnashyk', filter=Q(yarysgatnashyk__netije='yenis')),
        utuldy_sany=Count('yarysgatnashyk', filter=Q(yarysgatnashyk__netije='utuldy'))
    ).order_by('-yenis_sany')[:10]
    
    # Fakultet reýtingi (ýeňiş sany boýunça)
    fakultet_reytinqi = Fakultet.objects.annotate(
        yenis_sany=Count('oyuncu__yarysgatnashyk', filter=Q(oyuncu__yarysgatnashyk__netije='yenis')),
        utuldy_sany=Count('oyuncu__yarysgatnashyk', filter=Q(oyuncu__yarysgatnashyk__netije='utuldy')),
        oyuncu_sany=Count('oyuncu', filter=Q(oyuncu__aktiv=True)),
        umumy_gatnashyk=Count('oyuncu__yarysgatnashyk')
    ).order_by('-yenis_sany')[:5]
    
    # Sport görnüşleri boýunça statistika
    sport_gornusleri = SportGornushi.objects.annotate(
        yarys_sany=Count('yarys'),
        yenis_sany=Count('yarys__yarysgatnashyk', filter=Q(yarys__yarysgatnashyk__netije='yenis'))
    )[:5]
    
    context = {
        'umumy_oyuncu': umumy_oyuncu,
        'yenis_gazanan': yenis_gazanan,
        'yarys_sany': yarys_sany,
        'fakultet_sany': fakultet_sany,
        'sport_sany': sport_sany,
        'sonky_yaryslar': sonky_yaryslar,
        'oyuncular': oyuncular,
        'fakultet_reytinqi': fakultet_reytinqi,
        'sport_gornusleri': sport_gornusleri,
    }
    return render(request, 'sport_league/bas_sahypa.html', context)

def oyuncu_list(request):
    # Filtr parametrleri
    fakultet = request.GET.get('fakultet')
    sport = request.GET.get('sport')
    kurs = request.GET.get('kurs')
    search = request.GET.get('search')
    
    oyuncular = Oyuncu.objects.filter(aktiv=True).select_related('fakultet', 'esasgy_sport')
    
    # Filtrleri ulanylyşy
    if fakultet:
        oyuncular = oyuncular.filter(fakultet_id=fakultet)
    if sport:
        oyuncular = oyuncular.filter(sport_gornushi=sport)
    if kurs:
        oyuncular = oyuncular.filter(kurs=kurs)
    if search:
        oyuncular = oyuncular.filter(
            Q(ady__icontains=search) | 
            Q(familiyasy__icontains=search) | 
            Q(topar__icontains=search)
        )
    
    # Her oýunçy üçin ýeňiş sanyny goşmak
    oyuncular = oyuncular.annotate(
        yenis_sany=Count('yarysgatnashyk', filter=Q(yarysgatnashyk__netije='yenis'))
    )
    
    fakultetler = Fakultet.objects.all()
    sport_gornusleri = SportGornushi.objects.all()
    kurslar = range(1, 7)  # 1-6 kurslar
    
    context = {
        'oyuncular': oyuncular,
        'fakultetler': fakultetler,
        'sport_gornusleri': sport_gornusleri,
        'kurslar': kurslar,
        'selected_fakultet': fakultet,
        'selected_sport': sport,
        'selected_kurs': kurs,
        'search_query': search,
    }
    return render(request, 'sport_league/oyuncu_list.html', context)

def oyuncu_detail(request, pk):
    try:
        oyuncu = Oyuncu.objects.select_related('fakultet', 'esasgy_sport').prefetch_related(
            'sport_gornushi', 'oyuncusport_set'
        ).get(pk=pk, aktiv=True)
    except Oyuncu.DoesNotExist:
        raise Http404("Oýunçy tapylmady")
    
    yaryslar = YarysGatnashyk.objects.filter(oyuncu=oyuncu).select_related('yarys', 'yarys__sport_gornushi').order_by('-yarys__baslanjak_sene')
    
    # Statistika
    yenis_sany = yaryslar.filter(netije='yenis').count()
    utuldy_sany = yaryslar.filter(netije='utuldy').count()
    dowam_sany = yaryslar.filter(netije='dowam').count()
    umumy_gatnashyk = yaryslar.count()
    
    # Sport görnüşleri boýunça statistika
    sport_stat = {}
    for sport in oyuncu.sport_gornushi.all():
        sport_stat[sport.ady] = {
            'yarys_sany': yaryslar.filter(yarys__sport_gornushi=sport).count(),
            'yenis_sany': yaryslar.filter(yarys__sport_gornushi=sport, netije='yenis').count(),
        }
    
    # Üstünlik prosenti
    utus_prosenti = 0
    if umumy_gatnashyk > 0:
        utus_prosenti = round((yenis_sany / umumy_gatnashyk) * 100, 1)
    
    context = {
        'oyuncu': oyuncu,
        'yaryslar': yaryslar,
        'yenis_sany': yenis_sany,
        'utuldy_sany': utuldy_sany,
        'dowam_sany': dowam_sany,
        'umumy_gatnashyk': umumy_gatnashyk,
        'utus_prosenti': utus_prosenti,
        'sport_stat': sport_stat,
    }
    return render(request, 'sport_league/oyuncu_detail.html', context)

def yarys_list(request):
    # Filtr parametrleri
    status = request.GET.get('status')
    sport = request.GET.get('sport')
    search = request.GET.get('search')
    
    yaryslar = Yarys.objects.all().select_related('sport_gornushi')
    
    # Filtrler
    if status:
        yaryslar = yaryslar.filter(status=status)
    if sport:
        yaryslar = yaryslar.filter(sport_gornushi_id=sport)
    if search:
        yaryslar = yaryslar.filter(
            Q(ady__icontains=search) | 
            Q(yer__icontains=search)
        )
    
    # Her ýaryş üçin gatnaşyjylar sanyny goşmak
    yaryslar = yaryslar.annotate(
        gatnashyjylar_sany=Count('yarysgatnashyk'),
        yenijiler_sany=Count('yarysgatnashyk', filter=Q(yarysgatnashyk__netije='yenis'))
    ).order_by('-baslanjak_sene')
    
    sport_gornusleri = SportGornushi.objects.all()
    statuslar = Yarys.STATUS_CHOICES
    
    context = {
        'yaryslar': yaryslar,
        'sport_gornusleri': sport_gornusleri,
        'statuslar': statuslar,
        'selected_status': status,
        'selected_sport': sport,
        'search_query': search,
    }
    return render(request, 'sport_league/yarys_list.html', context)

def yarys_detail(request, pk):
    try:
        yarys = Yarys.objects.select_related('sport_gornushi').get(pk=pk)
    except Yarys.DoesNotExist:
        raise Http404("Ýaryş tapylmady")
    
    gatnashyk = YarysGatnashyk.objects.filter(yarys=yarys).select_related(
        'oyuncu', 'oyuncu__fakultet'
    ).order_by('orun')
    
    # Statistika
    umumy_gatnashyk = gatnashyk.count()
    yenijiler = gatnashyk.filter(netije='yenis')
    yenilenler = gatnashyk.filter(netije='utuldy')
    dowam_edyan = gatnashyk.filter(netije='dowam')
    
    # Fakultetler boýunça statistika
    fakultet_stat = {}
    for g in gatnashyk:
        fakultet = g.oyuncu.fakultet
        if fakultet not in fakultet_stat:
            fakultet_stat[fakultet] = {'umumy': 0, 'yenis': 0}
        fakultet_stat[fakultet]['umumy'] += 1
        if g.netije == 'yenis':
            fakultet_stat[fakultet]['yenis'] += 1
    
    context = {
        'yarys': yarys,
        'umumy_gatnashyk': umumy_gatnashyk,
        'yenijiler': yenijiler,
        'yenilenler': yenilenler,
        'dowam_edyan': dowam_edyan,
        'fakultet_stat': fakultet_stat,
    }
    return render(request, 'sport_league/yarys_detail.html', context)

def statistika(request):
    # Fakultetler boýunça statistika
    fakultet_stat = Fakultet.objects.annotate(
        oyuncu_sany=Count('oyuncu', filter=Q(oyuncu__aktiv=True)),
        yenis_sany=Count('oyuncu__yarysgatnashyk', filter=Q(oyuncu__yarysgatnashyk__netije='yenis')),
        utuldy_sany=Count('oyuncu__yarysgatnashyk', filter=Q(oyuncu__yarysgatnashyk__netije='utuldy')),
        umumy_gatnashyk=Count('oyuncu__yarysgatnashyk')
    ).order_by('-yenis_sany')
    
    # Üstünlik prosentini hasaplamak
    for f in fakultet_stat:
        if f.umumy_gatnashyk > 0:
            f.utus_prosenti = round((f.yenis_sany / f.umumy_gatnashyk) * 100, 1)
        else:
            f.utus_prosenti = 0
    
    # Sport görnüşleri boýunça statistika
    sport_stat = SportGornushi.objects.annotate(
        oyuncu_sany=Count('oyuncu', distinct=True, filter=Q(oyuncu__aktiv=True)),
        yarys_sany=Count('yarys'),
        yenis_sany=Count('yarys__yarysgatnashyk', filter=Q(yarys__yarysgatnashyk__netije='yensis')),
        gatnashyk_sany=Count('yarys__yarysgatnashyk')
    ).order_by('-yarys_sany')
    
    # Umumy statistika
    umumy_stat = {
        'oyuncu': Oyuncu.objects.filter(aktiv=True).count(),
        'fakultet': Fakultet.objects.count(),
        'sport': SportGornushi.objects.count(),
        'yarys': Yarys.objects.count(),
        'gatnashyk': YarysGatnashyk.objects.count(),
        'yenis': YarysGatnashyk.objects.filter(netije='yenis').count(),
        'utuldy': YarysGatnashyk.objects.filter(netije='utuldy').count(),
    }
    
    # Kurslar boýunça statistika
    kurs_stat = []
    for kurs in range(1, 7):
        sayy = Oyuncu.objects.filter(aktiv=True, kurs=kurs).count()
        yenis = YarysGatnashyk.objects.filter(oyuncu__kurs=kurs, netije='yenis').count()
        kurs_stat.append({
            'kurs': kurs,
            'oyuncu_sany': sayy,
            'yenis_sany': yenis,
        })
    
    context = {
        'fakultet_stat': fakultet_stat,
        'sport_stat': sport_stat,
        'umumy_stat': umumy_stat,
        'kurs_stat': kurs_stat,
    }
    return render(request, 'sport_league/statistika.html', context)

def fakultet_list(request):
    fakultetler = Fakultet.objects.annotate(
        yenis_sany=Count('oyuncu__yarysgatnashyk', filter=Q(oyuncu__yarysgatnashyk__netije='yenis')),
        utuldy_sany=Count('oyuncu__yarysgatnashyk', filter=Q(oyuncu__yarysgatnashyk__netije='utuldy')),
        oyuncu_sany=Count('oyuncu', filter=Q(oyuncu__aktiv=True)),
        umumy_gatnashyk=Count('oyuncu__yarysgatnashyk')
    ).order_by('-yenis_sany')
    
    context = {
        'fakultetler': fakultetler,
    }
    return render(request, 'sport_league/fakultet_list.html', context)

def fakultet_detail(request, pk):
    fakultet = get_object_or_404(Fakultet, pk=pk)
    
    oyuncular = Oyuncu.objects.filter(fakultet=fakultet, aktiv=True).annotate(
        yenis_sany=Count('yarysgatnashyk', filter=Q(yarysgatnashyk__netije='yenis'))
    ).order_by('-yenis_sany')
    
    yaryslar = YarysGatnashyk.objects.filter(
        oyuncu__fakultet=fakultet
    ).select_related('yarys', 'oyuncu').order_by('-yarys__baslanjak_sene')[:10]
    
    # Statistika
    umumy_yenis = YarysGatnashyk.objects.filter(oyuncu__fakultet=fakultet, netije='yenis').count()
    umumy_utuldy = YarysGatnashyk.objects.filter(oyuncu__fakultet=fakultet, netije='utuldy').count()
    umumy_gatnashyk = YarysGatnashyk.objects.filter(oyuncu__fakultet=fakultet).count()
    
    context = {
        'fakultet': fakultet,
        'oyuncular': oyuncular,
        'yaryslar': yaryslar,
        'umumy_yenis': umumy_yenis,
        'umumy_utuldy': umumy_utuldy,
        'umumy_gatnashyk': umumy_gatnashyk,
    }
    return render(request, 'sport_league/fakultet_detail.html', context)

def reyting(request):
    # Fakultet reýtingi
    fakultet_reytinqi = Fakultet.objects.annotate(
        yenis_sany=Count('oyuncu__yarysgatnashyk', filter=Q(oyuncu__yarysgatnashyk__netije='yenis')),
        utuldy_sany=Count('oyuncu__yarysgatnashyk', filter=Q(oyuncu__yarysgatnashyk__netije='utuldy')),
        oyuncu_sany=Count('oyuncu', filter=Q(oyuncu__aktiv=True)),
        umumy_gatnashyk=Count('oyuncu__yarysgatnashyk')
    ).order_by('-yenis_sany')
    
    # Oýunçy reýtingi
    oyuncu_reytinqi = Oyuncu.objects.filter(aktiv=True).annotate(
        yenis_sany=Count('yarysgatnashyk', filter=Q(yarysgatnashyk__netije='yenis')),
        utuldy_sany=Count('yarysgatnashyk', filter=Q(yarysgatnashyk__netije='utuldy')),
        umumy_gatnashyk=Count('yarysgatnashyk')
    ).order_by('-yenis_sany')[:50]
    
    context = {
        'fakultet_reytinqi': fakultet_reytinqi,
        'oyuncu_reytinqi': oyuncu_reytinqi,
    }
    return render(request, 'sport_league/reyting.html', context)