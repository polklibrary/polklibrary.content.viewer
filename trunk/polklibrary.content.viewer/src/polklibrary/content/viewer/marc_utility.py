
from polklibrary.content.viewer.utility import VendorInfo
from pymarc import MARCReader, Record, Field
import sys
import csv
import re



# SAVE -- solid useful function
# def inject__get_field_safe(rec, field, subfield=None, format_field=True, default=''):
    # if field in rec:
        # if subfield:
            # if subfield in rec[field]:
                # return rec[field][subfield]
            # else: 
                # return default
        # if format_field:
            # return rec[field].format_field()
        # else:
            # return rec[field]
    # return default
#Record.get_field_safe = inject__get_field_safe # inject


def inject__get_subfield(rec, subfield, default=''):
    if subfield and subfield in rec:
        return rec[subfield]
    return default
Field.get_subfield = inject__get_subfield # inject

def clean_spaces(text):
    return re.sub(' +', ' ', text)
    
def replace_marc_extras(text, exclude_list, default=''):
    for i in exclude_list:
        text = text.replace(i, default)
    return text.strip()
    
    
def process_marc(marc_stream):
    
    header = ['filmID', 'creator', 'title', 'date_of_publication', 'runtime', 'series_title', 'summary', 'format_type', 'associated_entity', 'geography', 'subject_group', 'genre', 'image_url', 'direct_url']
    exclude_genre = ['lcgft','Internet videos.', 'Videorecording']
    exclude_general = ['1 online resource', '(', ')', '1 video file', '1 streaming video file', '1 streaming', 'video', 'stereo', 'file', 'online resource','sound', 'digital', 'flv', 'online', 'color', 'and', 'streaming video file','streaming video files', '+', 'instructional', 'materials', 'sd', 'col', 'sd col digital file', '1 streaming video', '1 electronic resource', 'streaming', 'approximately', ',', '.', ':']
    
    index = 0
    max_process_index = 100000000
    #max_process_index = 100
    
    output = []
    reader = MARCReader(marc_stream)
    for rec in reader:
        index+=1
        if index > max_process_index:
            break
            
            
        #print('-----')
        
        record_id = ''
        for field in rec.get_fields('001'):
            id = field.format_field()
            if id:
                record_id = id
                break

        record_creator = ''
        for field in rec.get_fields('100'):
            creator = field.format_field().strip().rstrip('.,;:-/ ')
            if creator:
                record_creator = creator
                break
        
        record_summary = ''
        for field in rec.get_fields('520'):
            summary = field.get_subfield('a')
            if summary:
                record_summary = summary
                break
        
        record_date = ''
        for field in rec.get_fields('260'):
            datefield = field.get_subfield('c').strip().rstrip('.,;:-/ ')
            if datefield:
                record_date = datefield
                break
        
        record_runtime = ''
        for field in rec.get_fields('300'):
            runtime = replace_marc_extras(field.get_subfield('a'), exclude_general).strip().rstrip('.,;:-/ ')
            if runtime:
                record_runtime = runtime
                break
        
        
        
        # title
        record_title = ''
        record_full_title = ''
        subtitle = '';
        part = '';
        number = '';
        for field in rec.get_fields('245'):
            title = field.get_subfield('a').replace('"','').strip().rstrip(',.;:-=/ ')
            title = title[:1].upper() + title[1:] # capitalize first letter
            subtitle = field.get_subfield('b').strip().rstrip(',.;:-=/ ')
            subtitle = subtitle[:1].upper() + subtitle[1:] # capitalize first letter
            part = field.get_subfield('n').strip().rstrip(',.;:-=/ ')
            part = part[:1].upper() + part[1:] # capitalize first letter
            number = field.get_subfield('p').strip().rstrip(',.;:-=/ ')
            number = number[:1].upper() + number[1:] # capitalize first letter
            
            title_len_threshold = 50
            if title:
                record_title = title
                record_full_title = record_title
                if subtitle and len(subtitle) <= title_len_threshold:
                    record_full_title += '. ' + subtitle 
                if number and len(number) <= title_len_threshold:
                    record_full_title += '. ' + number 
                if part and len(part) <= title_len_threshold:
                    record_full_title += '. ' + part 
                    
                record_full_title = record_full_title.replace('=', ' ')
                record_full_title = re.sub(' +', ' ', record_full_title) # ensure one white space, after = replacing
                record_full_title = record_full_title.replace(' : ', ': ')
                record_full_title = record_full_title.replace(' . ', '. ')
                record_full_title = record_full_title.replace('..', '.')
                record_full_title = record_full_title.replace('?.', '?')
                record_full_title = record_full_title.replace('!.', '!')
                record_full_title = record_full_title.strip().rstrip('.,;:-=/ ')
                break
                
                
        # Series
        record_series = set()
        for field in rec.get_fields('490'):
            series = field.get_subfield('a').strip().rstrip('.,;:-=/ ')
            if series:
                record_series.add(series)
        record_series = list(record_series) 
        if len(record_series) == 0: # if no series exists, try to create it
            if (len(number) > 0 or len(part) > 0):
                record_series.append(record_title)
            
            
        # geography
        record_geography = set()
        for field in rec.get_fields('650'):
            geography = field.get_subfield('z').strip().rstrip('.,;:-=/ ')
            if geography:
                #print('650z: ' + geography)
                record_geography.add(geography)
        for field in rec.get_fields('651'):
            geography = field.get_subfield('a').strip().rstrip('.,;:-=/ ')
            if geography:
                #print('651a: ' + geography)
                record_geography.add(geography)
        record_geography = list(record_geography)
            
        # Genre            
        record_genre = set()
        for field in rec.get_fields('655'):
            genre = replace_marc_extras(field.get_subfield('a'), exclude_genre).strip().rstrip('.,;:-=/ ')
            if genre:
                record_genre.add(genre)
                #print('655: ' + genre)
        record_genre = list(record_genre)
        
        #associated entity
        record_associated_entity = set()
        for field in rec.get_fields('600'):
            for subfield_content in field.get_subfields('a','b','c'):
                associated_entity = subfield_content.strip().rstrip('.,;:-=/ ')
                if associated_entity:
                    record_associated_entity.add(associated_entity)
                    #print('600a-c: ' + associated_entity)
        for field in rec.get_fields('610'):
            for subfield_content in field.get_subfields('a','b','c'):
                associated_entity = subfield_content.strip().rstrip('.,;:-=/ ')
                if associated_entity:
                    record_associated_entity.add(associated_entity)
                    #print('610a-c: ' + associated_entity)
        record_associated_entity = list(record_associated_entity)
                    
        # subject groups
        record_subject_groups = set()
        for field in rec.get_fields('650'):
            for subfield in field:
                if subfield[0] and subfield[0] in ['a','b','c']:
                    subject = subfield[1].strip().rstrip('.,;:-=/ ')
                    if subject:
                        record_subject_groups.add(subject)
                        #print('650' + subfield[0] + ': ' + subject)
        record_subject_groups = list(record_subject_groups)
                            
        # URLS
        record_direct_url = ''
        record_image_url = ''
        for field in rec.get_fields('856'):
            ela_desc = field.get_subfield('z').lower()
            #print('856z: ' + ela_desc)
            ela_url = field.get_subfield('u')
            #print('856u: ' + ela_url)
            
            if 'image' in ela_desc or 'thumbnail' in ela_desc:
                record_image_url = ela_url
            else:
                record_direct_url = ela_url #assume it is a link
        
        
        record_vendor_id = 'unknown- ' + str(record_id)
        if 'aspresolver.com' in record_direct_url:
            record_vendor_id = VendorInfo.ALEXANDER_STREET_TARGET + (str(record_id).replace('asp',''))
        elif 'fod.infobase.com' in record_direct_url:
            record_vendor_id = VendorInfo.FILMSONDEMAND_TARGET + (str(record_id).replace('fod',''))
        elif 'kanopy.com' in record_direct_url:
            record_vendor_id = VendorInfo.KANOPY_TARGET + str(re.sub("[^0-9]", "", record_id)) # strip kan form original id
        elif 'docuseek2.com' in record_direct_url:
            record_vendor_id = VendorInfo.DOCUSEEK_TARGET + (str(record_id).replace('doc',''))
        
            
        output.append([
            record_vendor_id,
            record_creator,
            record_full_title,
            record_date,
            record_runtime,
            record_series,
            record_summary,
            'stream',
            record_associated_entity,
            record_geography,
            record_subject_groups,
            record_genre,
            record_image_url,
            record_direct_url,
        ])
     
    # for o in output:
        # print('-------------------------------------')
        # for r in o:
            # print(r)
     
    return header, output



# BELOW IS PATRICK's CODE -------------------------------------------------------------------------------------------------------

#global country_homophones
#country_homophones = ['Bury','March','Marks','Graham','Bo','Rosenberg','Graham','University','Kansas','Lawrence','Allen','Eugene','Brecht','Bentley','Man','Warren','Most','Regina','Cork','Highland','Flores','Elizabeth','Marshall','Americana','Police','Young','Wilson','Of','Fishers','Darwin','Martin','Bradford','Spring','Pop','Born','Bear','Mary','Bell','Mao','Temple','Along','Sherman','Much','Quincy','Paris','Paradise','Roman','Chor','Guilford','Johnson','Latina','Jackson','Summit','Gay','Male','Federal','Eden','Chekhov','Hayes','Reading','Boom','Barking','Tara','Alice','Harper','Barry','Nigel','Dale','Gary','David','Best','Split','Anna','Fleet','Pen','Carol','Lynn','Alicia','Nikki','Donna','Stuart','George','SIM','Sale','Enterprise','Charlotte','Barking','Tracy','Peer','PISA','Clive','Salt','Roy','Howard','Estelle','Helena','Working','Vic','Euclid','Allende','Normal','Asia','Obama','Iowa','Bronte','Nancy','Lakota','Melville','Rosario','Brad','Union','Liberty','Independence','Asia','Hercules','Wright','Clinton','Roman','Lucas','Savage','Goes','Gap','Jupiter','Taylor','Orion','Natal','Badger','Leatherhead','Roses','Batman','Griffith','Parker','Van','Rogers','Vista','Mustang','Montana','Chelsea','Mission','Dalton','Buy','Toledo','Gilbert','Evans','Oregon','Kansas','ABA','Bay','Tours','Leer','Sunrise','Imperial','Palm','The Valley','Dublin','Fountain','Kant','Plato','Ho','Norman','Bath','Honda','Toyota','Keller','Rye','Walker','Foster','Linda','Pace','Ode','Milton','Moss','Parole','Bar','Holden','Pearl','Lens','Date','Orange','Walnut','Atlantis','Davis','Homestead','Roth','Irving','OSA','UN','Green','Amos','Kyle','Palmer','Mon','Nice','Defiance','Wedding','Tire','Ron','Griffin','AUSA','Arnold','Bradley','Sebastian','Moe','Dome','Lice','Shaping','Bowie','Country Club','Bra','Central','Hull','Murray','Vincent','Anderson','Baron','Brits','Gardner','Ripley','Ariel','Lincoln','Opportunity','Oral','Manage','Sandy','Ramon','Converse','Gallup','Crystal','Humble','Wa','Mobile','Carson','Manga','Oss','Taft','Aloha','Crosby','Boo','Murphy','Gay','Newton','Moore','Inca','Perm','Ada','Metro','Eagle','Swords','Plunge','Derby','Hickory','Antony','Bryan','Cary','Beacon','Pinto','Turbo','Bartlett','Duncan','Vladimir','Mercedes','Bountiful','Dole','Sake','Edison','Stanley']


# #returns formatted string from pymarc field 
# def format_pymarc(i, index=0):
    # try:
        # text = i[index]
        # return text.format_field()
    # except AttributeError:
        # return ''
    # except IndexError:
        # return ''
# #get geographic subdividsions from subject headings 
# def read_geo_sub(record):
    # try:
        # geo_div = record['650']['z']
        # geo_div = geo_div.replace('.', '')
        # return geo_div 
    # except TypeError:
        # pass
    # except AttributeError:
        # pass 
# #get geographic subdividsions pt 2 
# def read_geo_head(record):
    # try:
        # geo_head = record['651']['a']
        # geo_head = geo_head.replace('.', '')
        # return geo_head 
    # except TypeError:
        # pass    
    # except AttributeError:
        # pass 
# #isolates topical terms in MARC subject headings 
# def read_topic(record):
    # topics = []
    # subj_list = record.get_fields('650')
    # for i in subj_list:
        # str = i.format_field()
        # if '--' in str:
            # tmp = str.split('--')
            # topics.append(tmp[0].strip())
        # else:
            # topics.append(str)
    # return topics         
# #test to see if a particular marc field is in record 
# def presence_test(rec, field, subfield):
    # try:
        # val = rec[field][subfield]
        # if val is not None:
            # return val
        # else:
            # return ''
    # except:
        # return ''
# #test to see if a particular marc field is in record 
# def fields_exist(rec, field, index):
    # try:
        # val = rec.get_fields(field)[index]
        # if val is not None:
            # return val
        # else:
            # return ''
    # except:
        # return ''
# #read a text file (not needed) 
# def read_text(f):
    # out = []
    # with open(f, 'r') as rf:
        # reader = csv.reader(rf)
        # for i in reader:
            # out.append(i)
    # return out         
# #remove particular substrings in list from a given string         
# def remove_substring(s, list):
    # for i in list:
        # s = s.replace(i, '')
    # return s

# #takes MARC record and returns csv file to be added to streaming video site 
    
# def build_rec(stream):
    # #exclude = [m for sub in exclude for m in sub]
    # global country_homophones
    # exclude = country_homophones
    # #print(exclude[0:10])
    # strip_list = ['1 online resource', '(', ')', '1 video file', '1 streaming video file', '1 streaming', 'video', 'stereo', 'file', 'online resource','sound', 'digital', 'flv', 'online', 'color', 'and', 'streaming video file','streaming video files', '+', 'instructional', 'materials', 'sd', 'col', 'sd col digital file', '1 streaming video', '1 electronic resource', 'streaming', 'approximately', ',', '.', ':']
    # genre_strip = ['lcgft','Internet videos.', 'Videorecording']
    # out_list = []
    # count = 0
    # geo_list = []
    # geo_headings = []
    # topics = []
    # has_geo = 0
    # #header = ['filmID', 'creator', 'title', 'date', 'phys_desc', 'series', 'summary', 'subj_person', 'subj_corp', 'rec_topics', 'rec_geo', 'genre', 'subj_person2']
    # header = ['filmID', 'creator', 'title', 'date_of_publication', 'runtime', 'series_title', 'summary', 'format_type', 'associated_entity', 'geography', 'subject_group', 'genre', 'image_url', 'direct_url']
    # out_list.append(header)
    # #with open(stream, 'rb') as rf:
    # reader = MARCReader(stream)#, to_unicode=True)
    # for rec in reader:
        # rec_geo = []
        # count += 1
        # vendor_name = ''
        # if count % 10000 == 0:
            # print('on record #' + str(count))
        # id = format_pymarc(rec.get_fields('001')).lower()
        # auth = format_pymarc(rec.get_fields('100'))
        # title = presence_test(rec, '245', 'a')
        # sub_title = presence_test(rec, '245', 'b')
        # part = presence_test(rec, '245', 'n')
        # number = presence_test(rec, '245', 'p')
        # date = presence_test(rec, '260', 'c')
        # title = title + ' ' + sub_title + ' ' + number + ' ' + part
        # title = title.replace('/', '')
        # tmp_title = title 
        # phys_desc = format_pymarc(rec.physicaldescription())
        # phys_desc = remove_substring(phys_desc, strip_list)
        # series = format_pymarc(rec.get_fields('490'))
       
        # if len(number) > 0 and len(series) == 0:
            # series = tmp_title
            # title.replace(series, '')
        # elif len(part) > 0 and len(series) == 0:
            # series = tmp_title
            # title.replace(series, '')
        # if ';' in series:
            # x = series.split(';')
            # series_name = x[0]
            # part_num = x[1]
            # title = title + ' ' + series_name + ' ' + part_num
            # series = series_name  
        
        # summary = format_pymarc(rec.get_fields('520'))
        # geo_text = GeoText(summary)
        # cities = geo_text.cities
        # for i in cities:
            # if i not in exclude:
                # rec_geo.append(i)        
        # #countries = list(geo_text.country_mentions)
        # #geo_cities = [cities, countries] 
        
        # subj_person = format_pymarc(rec.get_fields('600'))
        # subj_person = subj_person.replace('.', '')
        # subj_corp = format_pymarc(rec.get_fields('610'))
        # rec_topics = read_topic(rec)
        # rec_topics = [i.replace('.', '') for i in rec_topics]
        # set_rec_topics = set(rec_topics)
        # rec_topics = list(set_rec_topics)
        # if rec_topics is not None:
            # topics.append(rec_topics)
        # geo_terms = read_geo_sub(rec)
        # if geo_terms is not None:
            # geo_list.append(geo_terms)
            # rec_geo.append(geo_terms)            
        # geo_head = read_geo_head(rec)
        # if geo_head is not None:
            # geo_list.append(geo_head)
            # rec_geo.append(geo_head)
        # geo = format_pymarc(rec.get_fields('651'))
        # genre = format_pymarc(rec.get_fields('655'))
        # genre = remove_substring(genre, genre_strip)
        # subj_person2 = format_pymarc(rec.get_fields('700'))
        # rec_geo = list(set(rec_geo))
        
        
        
        
        
        
        # # attempt to retreive direct url and cover image url
        # url = ''
        # image_url = ''
        # if fields_exist(rec, '856', 0):
            # if 'image' in rec.get_fields('856')[0]['z'].lower() or 'thumbnail' in rec.get_fields('856')[0]['z'].lower():
                # image_url = rec.get_fields('856')[0]['u']
            # else:
                # url = rec.get_fields('856')[0]['u']
        # if fields_exist(rec, '856', 1):
            # if 'image' in rec.get_fields('856')[1]['z'].lower() or 'thumbnail' in rec.get_fields('856')[1]['z'].lower():
                # image_url = rec.get_fields('856')[1]['u']
        
        
        
        # try:
            # if 'aspresolver.com' in url:
                # id = 'asp' + id
                # vendor_name = 'astreet'
            # elif 'fod.infobase.com' in url:
                # id = 'fod' + id
                # vendor_name = 'fod'
            # elif 'kanopy.com' in url:
                # id2 = url.split('/')[-1]
                # id = 'kan' + id + '-' + id2 
                # vendor_name = 'kanopy'
            # else:
                # id = 'unknown' + id
                # vendor = 'unknown'
        # except:
            # id = 'unknown' + id
            # vendor = 'unknown'
            
        # # --- Patrick's ID
        # # try:
            # # id_test = int(id)
            # # id = 'fod' + id 
        # # except ValueError:
            # # if 'kan' in id:
                # # vendor_name = 'kanopy'
                # # id2 = url.split('/')[-1]
                # # id = id + '-' + id2 
            # # if 'asp' in id:
                # # vendor_name = 'astreet'        
        # associated_entities = subj_person + subj_corp   


        # #ensure lists
        # if isinstance(series, str):
            # if ',' in series:
                # series = series.split(',') # make a list
            # else:
                # series = [series.strip()] # make a list
        # if isinstance(genre, str):
            # if ',' in genre:
                # genre = genre.split(',') # make a list
            # else:
                # genre = [genre.strip()] # make a list
        # if isinstance(associated_entities, str):
            # if ',' in associated_entities:
                # associated_entities = associated_entities.split(',') # make a list
            # else:
                # associated_entities = [associated_entities] # make a list
        # if isinstance(rec_geo, str):
            # if ',' in rec_geo:
                # rec_geo = rec_geo.split(',') # make a list
            # else:
                # rec_geo = [rec_geo] # make a list
        # if isinstance(rec_topics, str):
            # if ',' in rec_topics:
                # rec_topics = rec_topics.split(',') # make a list
            # else:
                # rec_topics = [rec_topics] # make a list
        

        
        # tmp = [id, auth, title.strip(), date.strip(), phys_desc.strip(), series, summary.strip(), 'stream', associated_entities, rec_geo, rec_topics, genre, image_url, url]
            # #['filmID', 'creator', 'title', 'date_of_publication', 'runtime', 'series_title', 'summary', 'content_type', 'associated_entity', 'geography', 'subject', 'genre']
        # if '/aamr' not in id:
            # out_list.append(tmp)

    # return out_list, geo_list, topics           
                
# def search_summary(tup):
    # summary = tup[1]
    # subj = tup[0]
    # all_terms = []
    # for v in subj:
        # if '--' in v:
            # tmp = v.split('--')
            # for x in tmp:
                # x = x.replace('.', '')
                # all_terms.append(x)
        # else:
            # v = v.replace('.', '')
            # all_terms.append(v)
    # match_count = 0        
    # for item in all_terms:
        # if item in summary:
            # match_count += 1
        
    # final = [summary, subj, match_count]
    # return final  
    
    
# def pymarc_test(f):
    # with open(f, 'rb') as rf:
        # reader = MARCReader(rf)
        # for rec in reader:
            # try:
                # x = rec['651']['a']
                # print(x)
            # except TypeError:
                # pass

# def write_results(l):
    # #name = input('name your out file\n')
    # #name = name + '.csv'
    # name = 'done.csv'
    # with open(name, mode='wb') as f:
        # w = csv.writer(f, encoding='utf-8')
        # for row in l:
            # if len(row) > 0:
                # w.writerow(row)                

# def write_dict(d,s):
    # with open(s, 'w', encoding='utf-8', newline='') as f:
        # w = csv.writer(f)
        # w.writerow(['subject heading', 'total ct', 'astreet ct', 'kanopy ct', 'fod ct', 'unknown ct'])
        # for k, v in d.items():
            # cts = v
            # tmp = [k, cts[0], cts[1], cts[2], cts[3], cts[4]]
            # w.writerow(tmp)
            


# def clean(text):
    # text = text.rstrip('.')
    # text = text.replace('_', ' ')
    # text = re.sub(' +', ' ', text)

    # return text
    
# # def main():
    # # exclude = read_text(exclude_file)
    # # subj, geo, topics  = build_rec(file, exclude)
    # # print('geo terms detected: ' + str(len(geo)))
    # # print('topic terms detected: ' + str(len(topics)))
    # # write_results(subj)
    
# # main()
                
            
            
            
            
            
            
            
