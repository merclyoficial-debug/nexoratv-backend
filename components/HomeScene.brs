sub init()
    m.list = m.top.findNode("channels")
    m.player = m.top.findNode("player")

    m.list.observeField("itemSelected", "onChannelSelected")
    m.player.observeField("state", "onVideoStateChanged")

    m.streams = CreateObject("roAssociativeArray")

    ' Fonte publica temporaria para validar o player nativo Roku.

    ' Configure somente URLs diretas fornecidas pelo seu provedor.
    ' Exemplo de formato:
    ' addStream("Nome do canal", "https://servidor-autorizado/exemplo.m3u8", "hls")

    names = [
        "Premiere 2", "Premiere 3", "Premiere 4",
        "Premiere 5", "Premiere 7", "Premiere 8",
        "Premiere Clubes", "Sportv", "Sportv 2",
        "Sportv 3", "TNT", "TNT 2", "TNT Filmes e Séries",
        "TNT Novelas", "TNT Séries", "HBO", "HBO Mundi",
        "HBO Plus", "HBO Xtreme", "Megapix",
        "Paramount Network", "Space", "Telecine Action",
        "Telecine Cult", "Telecine Fun", "Telecine Pipoca",
        "Telecine Premium", "Telecine Touch", "Cartoon Network",
        "Discovery Kids", "Gloob", "Globinho", "Nick Júnior",
        "Nickelodeon", "Band News", "CNN Brasil", "Globo News",
        "Jovem Pan News", "Record News", "Globo Play Novelas",
        "Cinemax", "DAZN", "Disney +7", "Disney +8", "Disney +9",
        "Disney+", "Disney 2", "Disney 3", "Disney 4", "Disney 5",
        "ESPN", "ESPN 2", "ESPN 3", "ESPN 4", "ESPN 5", "GE TV",
        "Max", "Max 2", "Max 3", "Max 4", "Max 5",
        "N Sports", "Nosso Futebol", "Prime Video", "Prime Video 2",
        "Prime Video 3", "Apple TV 01", "Apple TV 02", "Apple TV 03",
        "Apple TV 04", "Apple TV 05", "Band Sports"
    ]

    content = CreateObject("roSGNode", "ContentNode")

    for each name in names
        item = content.createChild("ContentNode")
        item.title = name
    end for

    m.list.content = content
    m.list.visible = true
    m.player.visible = false
    m.list.setFocus(true)

    m.sourcesTask = CreateObject("roSGNode", "RokuSourcesTask")
    m.sourcesTask.baseUrl = "http://enzonic.com"
    m.sourcesTask.observeField("sources", "onSourcesLoaded")
    m.sourcesTask.observeField("error", "onSourcesError")
    m.top.appendChild(m.sourcesTask)
    m.sourcesTask.control = "RUN"
end sub


sub onSourcesLoaded()
    sources = m.sourcesTask.sources
    if sources = invalid then return

    content = m.list.content
    for each source in sources
        if source <> invalid then
            name = source.name
            url = source.url
            fmt = source.format
            if name <> invalid and url <> invalid and fmt <> invalid then
                if fmt = "hls" or fmt = "mp4" then
                    addStream(name, url, fmt)
                    found = false
                    childCount = content.getChildCount()
                    if childCount > 0 then
                        for i = 0 to childCount - 1
                            child = content.getChild(i)
                            if child.title = name then
                                found = true
                                exit for
                            end if
                        end for
                    end if
                    if not found then
                        newItem = CreateObject("roSGNode", "ContentNode")
                        newItem.title = name
                        content.insertChild(newItem, 0)
                    end if
                end if
            end if
        end if
    end for
    m.list.content = content
end sub


sub onSourcesError()
    message = m.sourcesTask.error
    if message = invalid or message = "" then
        message = "Nao foi possivel consultar o servidor Nexora."
    end if
    showMessage("Servidor Nexora", message)
end sub


sub addStream(name as String, url as String, fmt as String)
    info = CreateObject("roAssociativeArray")
    info.AddReplace("url", url)
    info.AddReplace("format", fmt)
    m.streams.AddReplace(name, info)
end sub


sub onChannelSelected()
    index = m.list.itemSelected

    if index < 0 then return

    item = m.list.content.getChild(index)
    if item = invalid then return

    name = item.title

    if not m.streams.DoesExist(name) then
        showMessage(name, "Este canal ainda nao possui uma URL direta de video configurada. A pagina embed nao e, por si so, um fluxo de video compativel com Roku.")
        return
    end if

    info = m.streams.Lookup(name)
    url = info.Lookup("url")
    fmt = info.Lookup("format")

    if url = invalid or url = "" or fmt = invalid or fmt = "" then
        showMessage(name, "A URL direta ou o formato do video esta faltando.")
        return
    end if

    videoContent = CreateObject("roSGNode", "ContentNode")
    videoContent.title = name
    videoContent.url = url
    videoContent.streamformat = fmt

    m.player.content = videoContent
    m.list.visible = false
    m.player.visible = true
    m.player.setFocus(true)
    m.player.control = "play"
end sub


sub onVideoStateChanged()
    state = m.player.state

    if state = "finished" then
        returnToList()
    else if state = "error" then
        returnToList()
        showMessage("Erro de reproducao", "A Roku nao conseguiu reproduzir esta fonte. Verifique a URL direta, o formato e os requisitos de acesso do provedor.")
    end if
end sub


sub returnToList()
    m.player.control = "stop"
    m.player.visible = false
    m.list.visible = true
    m.list.setFocus(true)
end sub


function onKeyEvent(key as String, press as Boolean) as Boolean
    if not press then return false

    if key = "back" and m.player.visible then
        returnToList()
        return true
    end if

    return false
end function


sub showMessage(title as String, message as String)
    dialog = CreateObject("roSGNode", "Dialog")
    dialog.title = title
    dialog.message = message
    dialog.buttons = ["OK"]
    m.top.dialog = dialog
end sub
