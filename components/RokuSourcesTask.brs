sub init()
    m.top.functionName = "fetchSources"
end sub


sub fetchSources()
    baseUrl = m.top.baseUrl
    if baseUrl = invalid or baseUrl = "" then
        m.top.error = "Endereco do servidor nao configurado."
        return
    end if

    transfer = CreateObject("roUrlTransfer")
    transfer.SetUrl(baseUrl + "/api/roku/sources")
    catalogText = transfer.GetToString()
    if catalogText = invalid or catalogText = "" then
        m.top.error = "Nao foi possivel acessar a API do servidor."
        return
    end if

    catalog = ParseJson(catalogText)
    if catalog = invalid then
        m.top.error = "O servidor retornou JSON invalido."
        return
    end if
    if catalog.sources = invalid then
        m.top.error = "A resposta nao contem a lista de fontes."
        return
    end if

    resolved = []
    for each entry in catalog.sources
        if entry <> invalid then
            sourceId = entry.id
            if sourceId <> invalid and sourceId <> "" then
                transfer.SetUrl(baseUrl + "/api/roku/sources/" + sourceId)
                detailText = transfer.GetToString()
                if detailText <> invalid and detailText <> "" then
                    details = ParseJson(detailText)
                    if details <> invalid then
                        source = details.source
                        if source <> invalid then
                            name = source.name
                            url = source.url
                            fmt = source.format
                            if name <> invalid and url <> invalid and fmt <> invalid then
                                if fmt = "hls" or fmt = "mp4" then
                                    resolved.Push(source)
                                end if
                            end if
                        end if
                    end if
                end if
            end if
        end if
    end for

    m.top.sources = resolved
    if resolved.Count() = 0 then
        m.top.error = "Nenhuma fonte direta HLS ou MP4 foi encontrada no servidor."
    end if
end sub
