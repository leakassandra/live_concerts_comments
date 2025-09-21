"""
Creates synthetic items via back-translation of underrepresented classes.
Languages used: German, French, Russian, Chinese, Italian, Spanish, Japanese, Arabic, Portuguese, Dutch.
Each minority class receives a new dataframe to which the back-translantions are appended. 
They are saved as seperate csv files in the current directory. The dataframes need to be merged again afterwards.
"""

import sys
import pandas as pd 
from transformers import MarianMTModel, MarianTokenizer

# get the original data frame to extract minority class
df = pd.read_csv(sys.argv[1])

# seperate classes, keeping all of their label-annotations 
class_to_augment = sys.argv[2]
class_to_augment_df = df[df[class_to_augment].isin(['X', 'x'])]

'''
Load the MarianMTModel.
'''
def load_translation_model(src_lang, tgt_lang):
    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
    # get model and tokanizer
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model

'''
Translate a single sentence.
'''
def translate(text, tokenizer, model):
    batch = tokenizer([text], return_tensors="pt", padding=True)
    generated = model.generate(**batch)
    return tokenizer.decode(generated[0], skip_special_tokens=True)

'''
Back-translate sentence (eng->german->en).
'''
def back_translate_en_de_en(text):
    # english -> german
    tok_en_de, mod_en_de = load_translation_model("en", "de")
    german_text = translate(text, tok_en_de, mod_en_de)
    # german -> english
    tok_de_en, mod_de_en = load_translation_model("de", "en")
    back_translated = translate(german_text, tok_de_en, mod_de_en)

    return back_translated

'''
Back-translate sentence (eng->french->en).
'''
def back_translate_en_fr_en(text):
    # english -> french
    tok_en_fr, mod_en_fr = load_translation_model("en", "fr")
    french_text = translate(text, tok_en_fr, mod_en_fr)
    # french -> english
    tok_fr_en, mod_fr_en = load_translation_model("fr", "en")
    back_translated = translate(french_text, tok_fr_en, mod_fr_en)

    return back_translated

'''
Back-translate sentence (eng->russian->en).
'''
def back_translate_en_ru_en(text):
    # english -> russian
    tok_en_ru, mod_en_ru = load_translation_model("en", "ru")
    russian_text = translate(text, tok_en_ru, mod_en_ru)
    # russian -> english
    tok_ru_en, mod_ru_en = load_translation_model("ru", "en")
    back_translated = translate(russian_text, tok_ru_en, mod_ru_en)

    return back_translated

'''
Back-translate sentence (eng->chinese->en).
'''
def back_translate_en_zh_en(text):
    # english -> chinese
    tok_en_zh, mod_en_zh = load_translation_model("en", "zh")
    chinese_text = translate(text, tok_en_zh, mod_en_zh)
    # chinese -> english
    tok_zh_en, mod_zh_en = load_translation_model("zh", "en")
    back_translated = translate(chinese_text, tok_zh_en, mod_zh_en)

    return back_translated

'''
Back-translate sentence (eng->italian->en).
'''
def back_translate_en_it_en(text):
    # english -> italian
    tok_en_it, mod_en_it = load_translation_model("en", "it")
    italian_text = translate(text, tok_en_it, mod_en_it)
    # italian -> english
    tok_it_en, mod_it_en = load_translation_model("it", "en")
    back_translated = translate(italian_text, tok_it_en, mod_it_en)

    return back_translated

'''
Back-translate sentence (eng->spanish->en).
'''
def back_translate_en_es_en(text):
    # english -> spanish
    tok_en_es, mod_en_es = load_translation_model("en", "es")
    spanish_text = translate(text, tok_en_es, mod_en_es)
    # spanish -> english
    tok_es_en, mod_es_en = load_translation_model("es", "en")
    back_translated = translate(spanish_text, tok_es_en, mod_es_en)

    return back_translated

'''
Back-translate sentence (eng->japanese->en).
'''
def back_translate_en_ja_en(text):
    # english -> japanese
    tok_en_ja, mod_en_ja = load_translation_model("en", "ja")
    japanese_text = translate(text, tok_en_ja, mod_en_ja)
    # japanese -> english
    tok_ja_en, mod_ja_en = load_translation_model("ja", "en")
    back_translated = translate(japanese_text, tok_ja_en, mod_ja_en)

    return back_translated

'''
Back-translate sentence (eng->arabic->en).
'''
def back_translate_en_ar_en(text):
    # english -> arabic
    tok_en_ar, mod_en_ar = load_translation_model("en", "ar")
    arabic_text = translate(text, tok_en_ar, mod_en_ar)
    # arabic -> english
    tok_ar_en, mod_ar_en = load_translation_model("ar", "en")
    back_translated = translate(arabic_text, tok_ar_en, mod_ar_en)

    return back_translated

'''
Back-translate sentence (eng->portoguese->en).
'''
def back_translate_en_pt_en(text):
    # english -> portoguese
    tok_en_pt, mod_en_pt = load_translation_model("en", "pt")
    portuguese_text = translate(text, tok_en_pt, mod_en_pt)
    # portuguese -> english
    tok_pt_en, mod_pt_en = load_translation_model("pt", "en")
    back_translated = translate(portuguese_text, tok_pt_en, mod_pt_en)

    return back_translated

'''
Back-translate sentence (eng->dutch->en).
'''
def back_translate_en_nl_en(text):
    # english -> dutch
    tok_en_nl, mod_en_nl = load_translation_model("en", "nl")
    dutch_text = translate(text, tok_en_nl, mod_en_nl)
    # dutch -> english
    tok_nl_en, mod_nl_en = load_translation_model("nl", "en")
    back_translated = translate(dutch_text, tok_nl_en, mod_nl_en)

    return back_translated

'''
Create new dataframe with back-translated messages.
'''
def create_bt_df(df, bt_func, lang_label):
    # model only accepts inputs <= 512
    df_bt = df[df['message'].str.len() <= 512].copy()
    df_bt['message'] = df_bt['message'].apply(bt_func)
    df_bt['bt_lang'] = lang_label  # track which language was used
    return df_bt

'''
Augment new dataframes.
'''
def augment_df(in_df, out_csv):
    # get original data frame
    original_df = in_df.copy()
    original_df['bt_lang'] = 'en'  # optional tag

    # get all back-translated data frames
    bt_ger_df = create_bt_df(in_df, back_translate_en_de_en, 'de')
    bt_fr_df  = create_bt_df(in_df, back_translate_en_fr_en, 'fr')
    bt_ru_df  = create_bt_df(in_df, back_translate_en_ru_en, 'ru')
    bt_zh_df  = create_bt_df(in_df, back_translate_en_zh_en, 'zh')
    bt_it_df  = create_bt_df(in_df, back_translate_en_it_en, 'it')
    bt_es_df  = create_bt_df(in_df, back_translate_en_it_en, 'es')
    bt_ja_df  = create_bt_df(in_df, back_translate_en_it_en, 'ja')
    bt_ar_df  = create_bt_df(in_df, back_translate_en_it_en, 'ar')
    bt_pt_df  = create_bt_df(in_df, back_translate_en_it_en, 'pt')
    bt_nl_df  = create_bt_df(in_df, back_translate_en_it_en, 'nl')

    # concat all into one data frame
    augmented_df = pd.concat([
        original_df,
        bt_ger_df,
        bt_fr_df,
        bt_ru_df,
        bt_zh_df,
        bt_it_df,
        bt_es_df,
        bt_ja_df,
        bt_ar_df,
        bt_pt_df,
        bt_nl_df
    ], ignore_index=True)
    # save as new file
    augmented_df.to_csv(out_csv, index=False)

# augment the data
augment_df(class_to_augment_df,sys.argv[3])
