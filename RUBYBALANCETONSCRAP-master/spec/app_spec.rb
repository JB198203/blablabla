require_relative '../lib/app.rb'

describe "the dark trader function" do
    it "should return an answer" do
        expect(crypto_scrapper).not_to be_nil
    end
    it "should be an Hash" do
        expect(crypto_scrapper).to be_a(Hash)
    end
end