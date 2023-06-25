import flag
from countryinfo import CountryInfo

from AltronRobot import dispatcher
from AltronRobot import telethn
from AltronRobot.events import register


@register(pattern="^/country (.*)")
async def msg(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    lol = input_str
    country = CountryInfo(lol)
    try:
        a = country.info()
    except:
        await event.reply("» ᴄᴏᴜɴᴛʀʏ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴜʀʀᴇɴᴛʟʏ")
    name = a.get("name")
    bb = a.get("altSpellings")
    hu = ""
    for p in bb:
        hu += p + ",  "

    area = a.get("area")
    borders = ""
    hell = a.get("borders")
    for fk in hell:
        borders += fk + ",  "

    call = ""
    WhAt = a.get("callingCodes")
    for what in WhAt:
        call += what + "  "

    capital = a.get("capital")
    currencies = ""
    fker = a.get("currencies")
    for FKer in fker:
        currencies += FKer + ",  "

    HmM = a.get("demonym")
    geo = a.get("geoJSON")
    pablo = geo.get("features")
    Pablo = pablo[0]
    PAblo = Pablo.get("geometry")
    EsCoBaR = PAblo.get("type")
    iso = ""
    iSo = a.get("ISO")
    for hitler in iSo:
        po = iSo.get(hitler)
        iso += po + ",  "
    fla = iSo.get("alpha2")
    nox = fla.upper()
    okie = flag.flag(nox)

    languages = a.get("languages")
    lMAO = ""
    for lmao in languages:
        lMAO += lmao + ",  "

    nonive = a.get("nativeName")
    waste = a.get("population")
    reg = a.get("region")
    sub = a.get("subregion")
    tik = a.get("timezones")
    tom = ""
    for jerry in tik:
        tom += jerry + ",   "

    GOT = a.get("tld")
    lanester = ""
    for targaryen in GOT:
        lanester += targaryen + ",   "

    wiki = a.get("wiki")

    caption = f"""» <b><u>Information Gathered Successfully</b></u>

‣ <b>Country Name :</b> {name}
‣ <b>Alternative Spellings :</b> {hu}
‣ <b>Country Area :</b> {area} square kilometers
‣ <b>Borders :</b> {borders}
‣ <b>Calling Codes :</b> {call}
‣ <b>Country's Capital :</b> {capital}
‣ <b>Country's currency :</b> {currencies}
‣ <b>Country's Flag :</b> {okie}
‣ <b>Demonym :</b> {HmM}
‣ <b>Country Type :</b> {EsCoBaR}
‣ <b>ISO Names :</b> {iso}
‣ <b>Languages :</b> {lMAO}
‣ <b>Native Name :</b> {nonive}
‣ <b>Population :</b> {waste}
‣ <b>Region :</b> {reg}
‣ <b>Sub Region :</b> {sub}
‣ <b>Time Zones :</b> {tom}
‣ <b>Top Level Domain :</b> {lanester}
‣ <b>Wikipedia :</b> {wiki}

<u>Information Gathered By {dispatcher.bot.first_name}</u>
"""

    await telethn.send_message(
        event.chat_id,
        caption,
        parse_mode="HTML",
        link_preview=None,
    )


__help__ = """
‣ ɪ ᴡɪʟʟ ɢɪᴠᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴀ ᴄᴏᴜɴᴛʀʏ
  ➲ /country <country name> : ɢᴀᴛʜᴇʀɪɴɢ ɪɴꜰᴏ ᴀʙᴏᴜᴛ ɢɪᴠᴇɴ ᴄᴏᴜɴᴛʀʏ
"""
__mod_name__ = "Cᴏᴜɴᴛʀʏ"