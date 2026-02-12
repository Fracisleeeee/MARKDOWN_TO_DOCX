local toc_enabled = true

local function meta_bool(meta, key, default)
  local v = meta[key]
  if v == nil then
    return default
  end
  if type(v) == "boolean" then
    return v
  end
  if type(v) == "string" then
    local s = string.lower(v)
    if s == "true" or s == "yes" or s == "1" then
      return true
    end
    if s == "false" or s == "no" or s == "0" then
      return false
    end
  end
  return default
end

function Meta(meta)
  toc_enabled = meta_bool(meta, "toc_enabled", true)
end

function Pandoc(doc)
  if not toc_enabled then
    return doc
  end

  -- Pandoc renders TOC before body for docx when --toc is enabled.
  -- Insert a page break at start of body so TOC stays on its own page.
  local pb = pandoc.RawBlock("openxml", '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
  table.insert(doc.blocks, 1, pb)
  return doc
end
