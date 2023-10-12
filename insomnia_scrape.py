

import requests
from bs4 import BeautifulSoup as bs
import datetime as dt
from datetime import *
from io import BytesIO
from PIL import Image
from urllib.parse import urljoin


number_of_pages_to_scrape = 15

sort_date = True # choose whether to sort items by date
sort_date_type = "NEWEST" # choose between "NEWEST" and "OLDEST" date items to show
date_to_compare : str = "2023-09-03-09-11" # YY-MM-DD-H-M

sort_phone = True # choose whether to sort items by phone model
iphone_model : str = "iPhone xs" # iPhone model
iphone_capacity : str = "64" # in GB

maximum_budget : float = 5900 # in euros


class ScrapeInsomnia(object):

    def __init__(self,
                 *args,
                 num_pages_to_scrape : int,
                 sort_by_date : bool,
                 sort_by_phone : bool,
                 all_iphone_models : list = ["iPhone", "iPhone 3G", "iPhone 3GS", "iPhone 4", "iPhone 4s"
                                             "iPhone 5", "iPhone 5c", "iPhone 5s", "iPhone 6", "iPhone 6 Plus",
                                             "iPhone 6s Plus", "iPhone 6s", "iPhone SE(1st generation)", "iPhone 7 Plus", 
                                             "iPhone 7", "iPhone 8 Plus", "iPhone 8", "iPhone X",
                                             "iPhone XR", "iPhone XS MAX", "iPhone XS", "iPhone 11",
                                             "iPhone 11 Pro Max", "iPhone 11 Pro", "iPhone SE(2nd generation)",
                                             "iPhone 12 Mini", "iPhone 12 Pro", "iPhone 12", "iPhone 12 Pro Max",
                                             "iPhone 13 Mini", "iPhone 13 Pro", "iPhone 13", "iPhone 13 Pro Max",
                                             "iPhone SE(3rd generation)", "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro",
                                             "iPhone 14 Pro Max", "iPhone 15 Pro Max", "iPhone 15 Pro", "iPhone 15",
                                             "iPhone 15 Plus"],
                 num_page : int = 1,
                 remove_str : str = "ΗΜΕΡΟΜΗΝΙΑ: ",
                 id_to_find : str = "ipsLayout_body",
                 class_to_find : str = "ipsClearfix",
                 current_date : dt.date = date.today(),
                 price_class : str = "ipsStream_price",
                 date_class : str = "ipsType_reset ipsType_normal",
                 type_of_product_class : str = "ipsBadge ipsBadge_positive",
                 description_class : str = "ipsSpacer_top ipsSpacer_half ipsType_richText ipsType_break ipsType_medium",
                 title_class : str = "ipsType_reset ipsContained_container ipsStreamItem_title ipsType_break",
                 keep_prices : list = [],
                 keep_titles : list = [],
                 filtered_prices : list = [],
                 filtered_titles : list = [],
                 final_titles : list = [],
                 final_prices : list = [],
                 final_result : dict = dict(),
                 ) -> None:

        self.all_iphone_models,self.num_pages_to_scrape, self.num_page, self.remove_str, self.id_to_find, self.class_to_find, \
            self.sort_by_date,self.sort_by_phone,self.current_date, self.price_class, self.date_class, \
                self.type_of_product_class, self.description_class, self.title_class, self.keep_prices, \
                    self.keep_titles, self.filtered_prices, self.filtered_titles, self.final_titles, self.final_prices, self.final_result= \
                    all_iphone_models, num_pages_to_scrape, num_page, remove_str, id_to_find, class_to_find, \
                        sort_by_date, sort_by_phone, current_date, price_class, date_class, type_of_product_class, \
                            description_class, title_class, keep_prices, keep_titles, filtered_prices, filtered_titles, \
                                final_titles, final_prices, final_result


        self.compare_date, self.date_filter = None, None
        self.iph_model = None
        cond = True

        if self.sort_by_phone:
            if self.sort_by_date:
                cond = len(args) >= 2
            else:
                cond = len(args) >= 1
        else:
            if self.sort_by_date:
                cond = len(args) == 2
            else:
                pass

        if not cond:
            raise ValueError(f"Expected more additional arguments (of type datetime.datetime) when sort_by_date and sort_by_phone boolean parameters are set to True")
        else:
            self.compare_date, self.date_filter = args[0], args[1]
            self.iph_model = args[2]
            self.iph_capacity = args[3] if len(args)>=4 else None
            self.max_budget = args[4] if len(args)>=5 else None




    def checkDate(self) -> bool:

        general_date : str = self.date.split(self.remove_str)[1] if self.date is not "N/A" else ""

        calendar_date : str = general_date[:10] if general_date else "1/1/1"

        timestamp_date : str = general_date[len(calendar_date)+1:] if general_date else "1:0 PM"
        timestamp_date : str = timestamp_date.replace("μμ","PM") if "μμ" in timestamp_date \
                                else timestamp_date.replace("πμ","AM") if "πμ" in timestamp_date \
                                    else timestamp_date

        timestamp_converted = datetime.strptime(timestamp_date.strip(), '%I:%M %p')

        insomnia_day,insomnia_month,insomnia_year = [int(k) for k in calendar_date.split("/")]
        insomnia_hour, insomnia_minute = int(timestamp_converted.hour), int(timestamp_converted.minute)

        post_date : dt.datetime = dt.datetime(year=insomnia_year,
                                              month=insomnia_month,
                                              day=insomnia_day,
                                              hour=insomnia_hour,
                                              minute=insomnia_minute)

        condition = post_date >= self.compare_date if self.date_filter is "NEWEST" else post_date <= self.compare_date if self.date_filter is "OLDEST" else False
        if self.compare_date is not None:return condition
        else:return True



# input_phone.split(" ")[1]
    def checkIphone(self) -> bool:

        input_phone : str = self.iph_model.lower()
        input_phone_type : str = input_phone.split(" ")[0]
        input_phone_number : str = "".join([k for k in input_phone if k.isdigit()]) # GET THE IPHONE NUMBER
        input_phone_details : str = input_phone.split(input_phone_number)[1] if input_phone_number else " ".join(input_phone.split(" ")[1:])
        input_phone_title : str = input_phone_type + " " + input_phone_number + input_phone_details



        iphone_name_condition = input_phone_title in self.title.lower()
        ## FILTER BY IPHONE NAME
        if self.title is not "N/A" and input_phone_title in [k.lower() for k in self.all_iphone_models]:
            # FILTER BY IPHONE CAPACITY (IF PROVIDED)
            if self.iph_capacity is not None:
                input_phone_capacity : str = self.iph_capacity.lower()
                if self.description is not "N/A":
                    return (input_phone_capacity in self.description.lower() or input_phone_capacity in self.title.lower()) and iphone_name_condition
                else:
                    return (input_phone_capacity in self.title.lower()) and iphone_name_condition
            else:
                return iphone_name_condition
        else:
            return True



    def main(self) -> None:
        for _url in [r"https://www.insomnia.gr/classifieds/search/?&q=iphone&type=classifieds_advert&page=" + str(k) + "&sortby=relevancy" for k in range(1,
                                                                                                                                                          self.num_pages_to_scrape+1)]:
            print(f"\nPAGE NUMBER {_url.split('page=')[1].split('&')[0]}:")

            page = requests.get(_url)
            soup = bs(page.content, "html.parser")
            res = soup.find(id=self.id_to_find)
            insomnia_posts = res.find_all("div", class_=self.class_to_find)



            # images = soup.select('div img')
            # print([images[i]["src"] for i in range(len(images))])
            # print(insomnia_posts)

            for post in insomnia_posts:
                links = post.find_all("")

                self.date = post.find("p",
                                 class_=self.date_class).text if post.find("p",class_=self.date_class) is not None else "N/A"

                price = post.find("span",
                                class_=self.price_class)

                type_of_product = post.find("span",
                                class_=self.type_of_product_class)

                self.description = post.find("div",
                                class_=self.description_class).text if post.find("div",class_=self.description_class) is not None else "N/A"

                self.title = post.find("h2",
                                class_=self.title_class).get_text(' | ', strip=True) if post.find("h2",class_=self.title_class) is not None else "N/A"

                image = post.find("img",
                                  class_ = "ipsImage ipsStream_image")


                if self.checkDate():
                    if self.checkIphone():
                        self.keep_titles.append(self.title)
                        self.keep_prices.append("".join([k for k in price.text if price is not None and k.isdigit()]))
                        self.keep_prices = [float(k) for k in self.keep_prices]

                        self.final_prices, self.final_titles = self.keep_prices, self.keep_titles

                        if self.max_budget is not None:
                            for title, price in zip(self.keep_titles,
                                                    self.keep_prices):
                                if price <= self.max_budget:
                                    self.filtered_prices.append(price)
                                    self.filtered_titles.append(title)
                                    self.final_prices, self.final_titles = self.filtered_prices, self.filtered_titles
                                else:self.final_prices, self.final_titles = [],[]
                        else:pass

                        self.final_result = {key : str(value) + " €" for key,value in zip(self.final_titles,
                                                                                          self.final_prices)}
                    else:pass
                else:pass


            self.get_everyPage_result()
        self.get_overall_result()



    def get_everyPage_result(self):
        r"""
        Prints a dictionary, with the title of the post as key and the price of it as a value (For every page scraped).
        """
        print(f"ITEMS FOUND: {self.final_result if self.final_result else None}")


    def get_overall_result(self):
        if self.final_result:
            most_worthy_phone : dict = {k[0] : k[1] for k in self.final_result.items() 
                                        if float(k[1].split(" €")[0]) == min(float(val.split(" €")[0]) for val in self.final_result.values())}
            print("\nOverall...")
            print(f"The matching iPhones with the lowest price are: {most_worthy_phone}")



if __name__ == "__main__":

    stop_year,stop_month,stop_day,stop_hour,stop_minute = [int(k) for k in date_to_compare.split("-")]

    assert int(iphone_capacity) in [2**i for i in range(3,10)], "The capacity of the selected iPhone has to be 8,16,32,64,128,256,512,... GB"
    iphone_capacity += " GB"

    scrape_insomnia = ScrapeInsomnia(
                                     dt.datetime(
                                                year=stop_year,
                                                month=stop_month,
                                                day=stop_day,
                                                hour=stop_hour,
                                                minute=stop_minute
                                                ),
                                    sort_date_type,
                                    iphone_model,
                                    iphone_capacity,
                                    maximum_budget,
                                    num_pages_to_scrape=number_of_pages_to_scrape,
                                    sort_by_date=sort_date,
                                    sort_by_phone=sort_phone
                                    )


    scrape_insomnia.main()




