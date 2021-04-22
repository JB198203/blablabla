require 'nokogiri'
require 'open-uri'
require 'pry'

def crypto_scrapper
    doc = Nokogiri::HTML(URI.open('https://coinmarketcap.com/all/views/all/'))

    symbol = Array.new
    price = Array.new

    doc.xpath('//tr/td[3]').each do |link|
        symbol << link.text
    end

    doc.xpath('//tr/td[5]').each do |link|
        price << link.text
    end

array_final = Hash[symbol.zip(price)]
end
puts crypto_scrapper