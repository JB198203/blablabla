require 'nokogiri'
require 'open-uri'
require 'pry'
require 'rubocop'


def city_scrapper(doc)
  ville = Array.new
  doc.xpath('//td/p/a').each do |v|
        ville << v.text
  end
  return ville
end

def mail_scrapper(doc,ville)
  # Tableau contenant les urls des villes
  url = Array.new
  # Tableau contenant les adresses mail
  email = Array.new

  for i in 0..ville.length-1
  #for i in 0..10
    url = "http://annuaire-des-mairies.com/95/" + CGI.escape(ville[i].downcase).gsub('+', '-') + ".html"
    docindex2 = Nokogiri::HTML(URI.open(url))
    tmp = Array.new
    docindex2.xpath('//td[contains(text(),"@")]').each do |e|
      email << e.text
      tmp << e.text
      #print(ville[i] + " : " + e.text + "\n")
    end
    # Permet de détecter si des villes ont des adresses mail (taille du tableau égale à 0)
    if tmp.length != 1
      # On ajoute une valeur par défaut
      print("[-] Aucune adresse mail trouvée pour la ville de " + ville[i] + "\n")
      email << "defaut@mail.fr"
    end
    
  end
  hash_final = Hash[ville.zip(email)]
  return hash_final
end

def perform(doc,docindex,url,ville,email)
  ville = city_scrapper(doc)
  mail_scrapper(doc,docindex,url,ville,email)
end

doc = Nokogiri::HTML(URI.open('http://annuaire-des-mairies.com/val-d-oise.html'))
ville = city_scrapper(doc)
hash_city_mail = mail_scrapper(doc, ville)
puts("[+] Affichage du hash ")
puts(hash_city_mail)