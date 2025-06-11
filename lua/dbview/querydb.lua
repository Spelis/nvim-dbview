local M = {}

M.apipath = (vim.fn.fnamemodify(debug.getinfo(1, "S").source:sub(2), ":h")) .. "/api.py"

local function getjson(dtype, db, query)
	local json = vim.fn.system({ "python", M.apipath, dtype, "query", db, query })
	return vim.fn.json_decode(json)
end

function M.sqlite(db, query)
	return getjson("sqlite", db, query)
end

return M
