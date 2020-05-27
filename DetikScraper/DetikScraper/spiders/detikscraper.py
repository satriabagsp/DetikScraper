# -*- coding: utf-8 -*-
import scrapy
import mysql.connector

class DetikscraperSpider(scrapy.Spider):
    name = 'detikscraper'
    pages = range(1, 1112)
    start_urls = []
    years = ('2018','2019','2020')
    katakuncis = ('pembunuhan','pencabulan','perbudakan','perampasan','pencurian','narkotika','penipuan','permusuhan')

    for katakunci in katakuncis:
        for year in years:
            for page in pages:
                link = 'https://www.detik.com/search/searchall?query='+katakunci+'&siteid=3&sortby=time&fromdatex=01/01/'+year+'&todatex=31/12/'+year+'&page='+str(page)
                start_urls.append(link)

    def parse(self, response):
        articles = response.css('div.list article a::attr(href)').getall()
        for article in articles:
            try:
                yield scrapy.Request(article, callback=self.parse_article)
            except:
                pass

    def parse_article(self, response):
        #konek db
        mydb = mysql.connector.connect(
            host = "localhost",
            user = "root",
            passwd = "",
            database = "berita_okezone"
            )
        mycursor = mydb.cursor()
        sumber = 'detik'
        keyword = 'kriminalitas'
        url = response.request.url
        
        #Declare variable tanggal
        tanggal = response.css('div.jdl div.date::text').get()
        if tanggal is None:
            tanggal = response.css('div.detail__header div.detail__date::text').get()
        elif len(tanggal) == 0:
            tanggal = response.css('div.jdl span.date::text').get()

        #Declare variable judul
        judul = response.css('div.jdl h1::text').get()
        if judul is None:
            judul = response.css('div.detail__header h1.detail__title::text').get()
            judul = " ".join(judul.split())
            
        #Declare variable konten
        tpt = response.css('div.detail_wrap div#detikdetailtext strong::text').get()
        kontens = response.css('div.detail_wrap div#detikdetailtext p::text').getall()
        if tpt is None:
            tpt = response.css('div.detail__body div.detail__body-text strong::text').get()
            kontens = response.css('div.detail__body div.detail__body-text::text').getall()
            if tpt is None:
                tpt = 'STRUKTUR PENULISAN BERBEDA'
                kontens = ('struktur','penulisan','berbeda')
        elif len(kontens) == 0:
            kontens = response.css('div.detail_wrap div#detikdetailtext::text').getall()
        tpt = tpt + '-'
        full = []
        tpt_bersih = tpt.strip()
        full.append(tpt_bersih)
        for kontenn in kontens:
            kontenn_bersih = kontenn.strip()
            full.append(kontenn_bersih)
        konten = ''.join(full)
        print('-',judul)
        
        #Masukin ke DB
        sql = "INSERT detik VALUES (%s, %s, %s, %s, %s, %s)"
        baris = (
            sumber,
            keyword, 
            url, 
            tanggal,
            judul,
            konten)

        mycursor.execute(sql, baris)
        mydb.commit()
