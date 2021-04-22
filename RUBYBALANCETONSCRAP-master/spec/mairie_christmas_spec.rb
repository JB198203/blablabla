require_relative '../lib/mairie_christmas.rb'

describe "the mail_scrapper function" do
    it "should return an array" do
        expect(mail_scrapper(doc,ville)).to be(Array)
    end
end