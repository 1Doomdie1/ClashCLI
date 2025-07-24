from click             import Choice
from pyclash           import ClansAPI
from prettytable       import PrettyTable
from typing_extensions import Annotated, List
from typer             import Typer, Context, Option, Argument


clan_typer = Typer(name = "clan")

OPTIONS = {
    "API_KEY": "",
    "OUTPUT_FORMAT": [
        "json", "table"
    ],
    "CTAG": None
}

@clan_typer.command(name = "list", help = "Pull a list of clans")
def list_(
    name:          Annotated[str,       Option(..., help = "Search clans by name")]                                                                                  = None,
    warFrequency:  Annotated[str,       Option(..., help = "Filter by clan war frequency")]                                                                          = None,
    locationId:    Annotated[int,       Option(..., help = "Filter by clan location identifier. For list of available locations, refer to getLocations operation.")] = None,
    minMembers:    Annotated[int,       Option(..., help = "Filter by minimum number of clan members")]                                                              = 2,
    maxMembers:    Annotated[int,       Option(..., help = "Filter by maximum number of clan members")]                                                              = None,
    minClanPoints: Annotated[int,       Option(..., help = "Filter by minimum amount of clan points.")]                                                              = None,
    minClanLevel:  Annotated[int,       Option(..., help = "Filter by minimum clan level.")]                                                                         = None,
    limit:         Annotated[int,       Option(..., help = "Limit the number of items returned in the response.")]                                                   = 10,
    after:         Annotated[str,       Option(..., help = "Return only items that occur after this marker.")]                                                       = None,
    before:        Annotated[str,       Option(..., help = "Return only items that occur before this marker.")]                                                      = None,
    labelIds:      Annotated[List[str], Option(..., help = "Comma separatered list of label IDs to use for filtering results.")]                                     = None,
    output_as:     Annotated[str,       Option(..., help = "Format results", click_type = Choice(OPTIONS["OUTPUT_FORMAT"]))]                                         = "table"
):
    clanAPI = ClansAPI(OPTIONS["API_KEY"])
    result = clanAPI.list(
        name          = name, 
        warFrequency  = warFrequency, 
        locationId    = locationId, 
        minMembers    = minMembers, 
        maxMembers    = maxMembers,
        minClanPoints = minClanPoints,
        minClanLevel  = minClanLevel,
        limit         = limit,
        after         = after,
        before        = before,
        labelIds      = labelIds
    )

    if result.status_code != 200:
        print(result.model_dump_json(indent = 4))
        exit()

    if output_as == "table":
        table = PrettyTable()
        table.field_names = ["Nr", "Tag", "Name", "Labels", "Location", "Type", "Members", "Points", "Level"]
        table.align = "l"

        for index, clan in enumerate(result.body.items, 1):
            table.add_row([
                index, 
                clan.tag,
                clan.name,
                ", ".join([i.name for i in clan.labels if i]),
                clan.location.name if clan.location else "None",
                clan.type,
                clan.members,
                clan.clanPoints,
                clan.clanLevel
            ])
        print(table)
    else:
        print(result.model_dump_json(indent = 4))

@clan_typer.command(help = "Get clan info.")
def info(
    output_as: Annotated[str, Option(..., help = "Format results", click_type = Choice(OPTIONS["OUTPUT_FORMAT"]))] = "table"
):
    clanAPI = ClansAPI(OPTIONS["API_KEY"])
    result = clanAPI.get(clanTag = OPTIONS["CTAG"])

    if result.status_code != 200:
        print(result.model_dump_json(indent = 4))
        exit()

    if output_as == "table":
        general_info_table = PrettyTable(["Key", "Value"])
        general_info_table.align = "l"
        general_info_table.add_rows([
            ["Tag",                   result.body.tag             ],
            ["Name",                  result.body.name            ],
            ["Members",               result.body.members         ],
            ["Min trophies to enter", result.body.requiredTrophies],
            ["Type",                  result.body.type            ],
            ["Location",              result.body.location.name   ],
            ["Badge",                 result.body.badgeUrls.large ],
            ["Description",           result.body.description     ],
        ])
        print("[+] General Info")
        print(f"{general_info_table}\n")

        clan_table = PrettyTable(["Key", "Value"])
        clan_table.align = "l"
        clan_table.add_rows([
            ["Level", result.body.clanLevel],
            ["Points", result.body.clanPoints],
            ["Builder Base Points", result.body.clanBuilderBasePoints],
            ["Capital Points", result.body.clanCapitalPoints],
            ["Capital League", result.body.capitalLeague.name]
        ])
        print("[+] Clan Info")
        print(f"{clan_table}\n")

        members_table = PrettyTable(["Clan Rank", "Tag", "Name", "Role", "Townhall Level", "Exp Level", "League", "Trophies"])
        members_table.align = "l"

        for member in result.body.memberList:
            members_table.add_row([
                member.clanRank,
                member.tag,
                member.name,
                member.role,
                member.townHallLevel,
                member.expLevel,
                member.league.name,
                member.trophies
            ])
        print("[+] Clan Members Info")
        print(members_table)
    else:
        print(result.model_dump_json(indent = 4))

@clan_typer.command(help = "Pull list of war logs")
def war_logs(
    limit:     Annotated[int, Option  (..., help = "Limit the number of items returned in the response."          )] = 10,
    after:     Annotated[str, Option  (..., help = "Return only items that occur after this marker."              )] = None,
    before:    Annotated[str, Option  (..., help = "Return only items that occur before this marker."             )] = None,
    output_as: Annotated[str, Option  (..., help = "Format results", click_type = Choice(OPTIONS["OUTPUT_FORMAT"]))] = "table"
):
    clanAPI = ClansAPI(OPTIONS["API_KEY"])
    result = clanAPI.war_log(
        clanTag = OPTIONS["CTAG"],
        limit   = limit,
        after   = after,
        before  = before
    )

    if result.status_code != 200:
        print(result.model_dump_json(indent = 4))
        exit()

    if output_as == "table":
        table = PrettyTable(["Nr", "Result", "E_Tag", "E_Name", "E_Level", "E_Stars", "A_Tag", "A_Name", "A_Level", "A_Stars", "End Time"])
        table.align = "l"
        for index, war in enumerate(result.body.items, 1):
            table.add_row([
                index,
                war.result,
                war.opponent.tag,
                war.opponent.name,
                war.opponent.clanLevel,
                war.opponent.stars,
                war.clan.tag,
                war.clan.name,
                war.clan.clanLevel,
                war.clan.stars,
                war.endTime
            ])
        print(table)
    else:
        print(result.model_dump_json(indent = 4))

@clan_typer.callback()
def callback(
    ctx:  Context,
    ctag: Annotated[str, Option(..., help = "Clan tag")] = None
):
    OPTIONS["API_KEY"] = ctx.obj.get("API_KEY")

    if ctx.invoked_subcommand in ("info", "war-logs") and not ctag:
        print("[-] Please provide the clan tag")
        print(f"    -> clash clan --ctag=<tag> {ctx.invoked_subcommand} (args) [flags]")
        exit()

    OPTIONS["CTAG"] = ctag
