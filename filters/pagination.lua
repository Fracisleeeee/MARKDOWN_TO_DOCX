local page_break_h1 = true
local toc_enabled = true
local seen_h1 = 0

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
  page_break_h1 = meta_bool(meta, "page_break_h1", true)
  toc_enabled = meta_bool(meta, "toc_enabled", true)
end

function Header(h)
  if not page_break_h1 or h.level ~= 1 then
    return nil
  end

  seen_h1 = seen_h1 + 1

  -- Skip first body H1 to avoid accidental leading blank pages.
  if seen_h1 == 1 then
    return nil
  end

  local pagebreak = pandoc.RawBlock(
    "openxml",
    '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
  )

  return { pagebreak, h }
end
