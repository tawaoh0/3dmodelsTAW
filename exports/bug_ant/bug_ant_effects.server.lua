--[[
	Effets mythiques — bug_ant
	Généré par build.py (3dmodelsTAW).

	Installation : placer ce Script directement dans le Model de la créature
	importée (à côté des MeshParts). Il :
	  • passe les pièces « *_Glow » en matériau Neon de la couleur de lueur ;
	  • ajoute une lumière qui pulse ;
	  • attache des particules à chaque os nommé « FX_* », selon le thème
	    de la créature (feu, acide, âmes, givre, abysses, sang, or).
]]

local TweenService = game:GetService("TweenService")

local model = script.Parent

local GLOW = Color3.fromRGB(125, 255, 74)
local GLOW_HOT = Color3.fromRGB(228, 255, 208)

local FIRE = "rbxasset://textures/particles/fire_main.dds"
local SMOKE = "rbxasset://textures/particles/smoke_main.dds"
local SPARKLES = "rbxasset://textures/particles/sparkles_main.dds"

-- Thèmes : émetteur principal + émetteur secondaire (braises, gouttes, flocons…)
local THEMES = {
	fire = {
		main = { texture = FIRE, accel = Vector3.new(0, 4, 0), speed = 1, rot = 90, light = 1 },
		extra = { name = "Embers", texture = SPARKLES, accel = Vector3.new(0, 2, 0),
			speed = NumberRange.new(1, 3), lifetime = NumberRange.new(0.8, 1.6), size = 0.25 },
	},
	acid = { -- bulles toxiques qui montent lentement + gouttes qui tombent
		main = { texture = SMOKE, accel = Vector3.new(0, 1.5, 0), speed = 0.4, rot = 30, light = 0.6 },
		extra = { name = "AcidDrips", texture = SPARKLES, accel = Vector3.new(0, -30, 0),
			speed = NumberRange.new(0, 0.3), lifetime = NumberRange.new(0.5, 0.9), size = 0.18 },
	},
	souls = { -- volutes spectrales qui ondulent vers le haut
		main = { texture = SMOKE, accel = Vector3.new(0, 2.5, 0), speed = 0.6, rot = 180, light = 0.8 },
		extra = { name = "Wisps", texture = SPARKLES, accel = Vector3.new(0, 1, 0),
			speed = NumberRange.new(0.5, 1.5), lifetime = NumberRange.new(1.5, 2.5), size = 0.3 },
	},
	frost = { -- brume froide qui retombe + flocons
		main = { texture = SMOKE, accel = Vector3.new(0, -1.5, 0), speed = 0.5, rot = 20, light = 0.5 },
		extra = { name = "Snow", texture = SPARKLES, accel = Vector3.new(0, -3, 0),
			speed = NumberRange.new(0.5, 1.5), lifetime = NumberRange.new(1.2, 2), size = 0.2 },
	},
	abyss = { -- lueurs bioluminescentes qui dérivent + bulles qui remontent
		main = { texture = SPARKLES, accel = Vector3.new(0, 0.6, 0), speed = 0.3, rot = 40, light = 1 },
		extra = { name = "Bubbles", texture = SMOKE, accel = Vector3.new(0, 4, 0),
			speed = NumberRange.new(0.5, 1.5), lifetime = NumberRange.new(1.5, 3), size = 0.12 },
	},
	blood = { -- nuage de sang qui s'étire et retombe lentement + petites bulles
		main = { texture = SMOKE, accel = Vector3.new(0, -0.8, 0), speed = 0.35, rot = 25, light = 0.4 },
		extra = { name = "Bubbles", texture = SPARKLES, accel = Vector3.new(0, 3, 0),
			speed = NumberRange.new(0.3, 1), lifetime = NumberRange.new(1, 2), size = 0.12 },
	},
	vent = { -- fumée noire des cheminées hydrothermales qui monte vite + braises
		main = { texture = SMOKE, accel = Vector3.new(0, 6, 0), speed = 1.2, rot = 60, light = 0.7 },
		extra = { name = "Embers", texture = SPARKLES, accel = Vector3.new(0, 3, 0),
			speed = NumberRange.new(1, 2.5), lifetime = NumberRange.new(1, 2), size = 0.2 },
	},
	lure = { -- points lumineux qui flottent lentement autour de l'appât + plancton
		main = { texture = SPARKLES, accel = Vector3.new(0, 0.2, 0), speed = 0.15, rot = 20, light = 1 },
		extra = { name = "Plankton", texture = SPARKLES, accel = Vector3.new(0, -0.3, 0),
			speed = NumberRange.new(0.1, 0.5), lifetime = NumberRange.new(2, 4), size = 0.08 },
	},
	moon = { -- éclats d'argent lunaires qui tombent lentement + brume froide qui rampe
		main = { texture = SPARKLES, accel = Vector3.new(0, -0.6, 0), speed = 0.3, rot = 30, light = 0.9 },
		extra = { name = "Mist", texture = SMOKE, accel = Vector3.new(0, -0.4, 0),
			speed = NumberRange.new(0.2, 0.6), lifetime = NumberRange.new(2, 3.5), size = 0.5 },
	},
	phoenix = { -- grandes flammes dorées qui montent + étincelles qui tourbillonnent
		main = { texture = FIRE, accel = Vector3.new(0, 6, 0), speed = 1.4, rot = 180, light = 1.2 },
		extra = { name = "Sparks", texture = SPARKLES, accel = Vector3.new(0, 5, 0),
			speed = NumberRange.new(2, 4), lifetime = NumberRange.new(0.6, 1.2), size = 0.15 },
	},
	magma = { -- fumée lourde qui monte lentement + gouttes de lave qui tombent
		main = { texture = SMOKE, accel = Vector3.new(0, 1.5, 0), speed = 0.5, rot = 15, light = 0.8 },
		extra = { name = "LavaDrips", texture = FIRE, accel = Vector3.new(0, -25, 0),
			speed = NumberRange.new(0, 0.5), lifetime = NumberRange.new(0.4, 0.8), size = 0.3 },
	},
	sulfur = { -- fumée de soufre qui rampe au sol + flammèches qui sautent
		main = { texture = SMOKE, accel = Vector3.new(0, 0.8, 0), speed = 0.4, rot = 20, light = 0.7 },
		extra = { name = "Flamelets", texture = FIRE, accel = Vector3.new(0, 4, 0),
			speed = NumberRange.new(0.5, 1.5), lifetime = NumberRange.new(0.3, 0.6), size = 0.35 },
	},
	hellfire = { -- grandes flammes cramoisies + cendres qui retombent
		main = { texture = FIRE, accel = Vector3.new(0, 7, 0), speed = 1.2, rot = 120, light = 1.1 },
		extra = { name = "Ash", texture = SMOKE, accel = Vector3.new(0, -1, 0),
			speed = NumberRange.new(0.3, 1), lifetime = NumberRange.new(1.5, 2.5), size = 0.2 },
	},
	aurora = { -- voiles d'aurore boréale qui ondulent vers le haut + neige fine
		main = { texture = SPARKLES, accel = Vector3.new(0, 1.2, 0), speed = 0.4, rot = 60, light = 1 },
		extra = { name = "Snow", texture = SPARKLES, accel = Vector3.new(0, -2, 0),
			speed = NumberRange.new(0.3, 1), lifetime = NumberRange.new(2, 3), size = 0.12 },
	},
	blizzard = { -- neige soufflée à l'horizontale + cristaux de givre
		main = { texture = SMOKE, accel = Vector3.new(6, -1, 0), speed = 1.5, rot = 40, light = 0.6 },
		extra = { name = "Snow", texture = SPARKLES, accel = Vector3.new(8, -2, 0),
			speed = NumberRange.new(2, 4), lifetime = NumberRange.new(0.8, 1.5), size = 0.12 },
	},
	wraith = { -- brume spectrale pâle qui monte lentement + éclats froids
		main = { texture = SMOKE, accel = Vector3.new(0, 0.6, 0), speed = 0.25, rot = 90, light = 0.7 },
		extra = { name = "Frost", texture = SPARKLES, accel = Vector3.new(0, -0.5, 0),
			speed = NumberRange.new(0.2, 0.6), lifetime = NumberRange.new(1.5, 3), size = 0.1 },
	},
	polar = { -- souffle glacé + gros flocons de la nuit polaire
		main = { texture = SMOKE, accel = Vector3.new(0, -0.5, 0), speed = 0.8, rot = 30, light = 0.6 },
		extra = { name = "Snowflakes", texture = SPARKLES, accel = Vector3.new(0, -1.5, 0),
			speed = NumberRange.new(0.3, 0.8), lifetime = NumberRange.new(2, 3.5), size = 0.22 },
	},
	crystal = { -- éclats de cristal qui scintillent + paillettes de givre qui tombent
		main = { texture = SPARKLES, accel = Vector3.new(0, 0.5, 0), speed = 0.6, rot = 200, light = 1.1 },
		extra = { name = "IceShards", texture = SPARKLES, accel = Vector3.new(0, -6, 0),
			speed = NumberRange.new(0.5, 1.5), lifetime = NumberRange.new(0.6, 1.2), size = 0.15 },
	},
	jungle = { -- spores lumineuses qui flottent + gouttes de poison turquoise
		main = { texture = SPARKLES, accel = Vector3.new(0, 0.4, 0), speed = 0.3, rot = 50, light = 0.9 },
		extra = { name = "Poison", texture = SMOKE, accel = Vector3.new(0, -8, 0),
			speed = NumberRange.new(0, 0.4), lifetime = NumberRange.new(0.5, 1), size = 0.18 },
	},
	quetzal = { -- plumes lumineuses portées par le vent + venin émeraude qui goutte
		main = { texture = SPARKLES, accel = Vector3.new(1.5, 1, 0), speed = 0.6, rot = 120, light = 1 },
		extra = { name = "Venom", texture = SMOKE, accel = Vector3.new(0, -10, 0),
			speed = NumberRange.new(0, 0.3), lifetime = NumberRange.new(0.4, 0.8), size = 0.15 },
	},
	ruins = { -- poussière d'or des ruines + feuilles qui tombent en tournoyant
		main = { texture = SPARKLES, accel = Vector3.new(0, 0.8, 0), speed = 0.5, rot = 90, light = 0.9 },
		extra = { name = "Leaves", texture = SMOKE, accel = Vector3.new(0.5, -1.2, 0),
			speed = NumberRange.new(0.3, 0.8), lifetime = NumberRange.new(2, 3), size = 0.25 },
	},
	orchid = { -- pollen lumineux qui tourbillonne + pétales qui tombent
		main = { texture = SPARKLES, accel = Vector3.new(0, 0.6, 0), speed = 0.5, rot = 160, light = 1 },
		extra = { name = "Petals", texture = SMOKE, accel = Vector3.new(0.4, -1, 0),
			speed = NumberRange.new(0.2, 0.6), lifetime = NumberRange.new(2, 3), size = 0.2 },
	},
	nightmare = { -- flammes spectrales vert poison qui lèchent vers le haut + braises
		main = { texture = FIRE, accel = Vector3.new(0, 3, 0), speed = 1, rot = 90, light = 1 },
		extra = { name = "Embers", texture = SPARKLES, accel = Vector3.new(0, 2, 0),
			speed = NumberRange.new(0.5, 1.5), lifetime = NumberRange.new(0.6, 1.2), size = 0.1 },
	},
	ravens = { -- plumes noires qui tombent en tournoyant + brume rouge sang
		main = { texture = SMOKE, accel = Vector3.new(0, 0.5, 0), speed = 0.3, rot = 60, light = 0.5 },
		extra = { name = "Feathers", texture = SPARKLES, accel = Vector3.new(0, -1.5, 0),
			speed = NumberRange.new(0.3, 1), lifetime = NumberRange.new(1.5, 3), size = 0.25 },
	},
	vampire = { -- gouttes de sang qui tombent + brume pourpre au ras du sol
		main = { texture = SMOKE, accel = Vector3.new(0, 0.2, 0), speed = 0.3, rot = 40, light = 0.6 },
		extra = { name = "BloodDrops", texture = SPARKLES, accel = Vector3.new(0, -6, 0),
			speed = NumberRange.new(0, 0.3), lifetime = NumberRange.new(0.5, 1), size = 0.12 },
	},
	soulweb = { -- âmes pâles prisonnières qui flottent + éclats de toile qui scintillent
		main = { texture = SMOKE, accel = Vector3.new(0, 1.5, 0), speed = 0.4, rot = 120, light = 0.9 },
		extra = { name = "WebGlints", texture = SPARKLES, accel = Vector3.new(0, 0, 0),
			speed = NumberRange.new(0, 0.2), lifetime = NumberRange.new(1, 2), size = 0.15 },
	},
	labyrinth = { -- poussière d'or du labyrinthe + éclats de pierre qui tombent
		main = { texture = SMOKE, accel = Vector3.new(0, 0.5, 0), speed = 0.4, rot = 30, light = 0.6 },
		extra = { name = "StoneChips", texture = SPARKLES, accel = Vector3.new(0, -4, 0),
			speed = NumberRange.new(0.5, 1.5), lifetime = NumberRange.new(0.6, 1.2), size = 0.12 },
	},
	ragnarok = { -- runes lumineuses qui s'envolent + souffle glacé du Fimbulvetr
		main = { texture = SMOKE, accel = Vector3.new(0, 1, 0), speed = 0.5, rot = 60, light = 0.7 },
		extra = { name = "RuneSparks", texture = SPARKLES, accel = Vector3.new(0, 2.5, 0),
			speed = NumberRange.new(0.5, 1.2), lifetime = NumberRange.new(1, 2), size = 0.18 },
	},
	duat = { -- sable doré qui s'écoule + esprits bleus du monde des morts
		main = { texture = SMOKE, accel = Vector3.new(0, -1, 0), speed = 0.4, rot = 45, light = 0.5 },
		extra = { name = "Spirits", texture = SPARKLES, accel = Vector3.new(0, 2, 0),
			speed = NumberRange.new(0.3, 0.9), lifetime = NumberRange.new(1.2, 2.2), size = 0.2 },
	},
	foxfire = { -- feux de renard qui flottent + pétales de cerisier
		main = { texture = FIRE, accel = Vector3.new(0, 1.5, 0), speed = 0.4, rot = 120, light = 1 },
		extra = { name = "Sakura", texture = SPARKLES, accel = Vector3.new(0.5, -1, 0),
			speed = NumberRange.new(0.3, 1), lifetime = NumberRange.new(1.5, 3), size = 0.15 },
	},
	petrify = { -- poussière de pierre + éclats verts du regard pétrifiant
		main = { texture = SMOKE, accel = Vector3.new(0, -0.5, 0), speed = 0.3, rot = 30, light = 0.4 },
		extra = { name = "GazeGlints", texture = SPARKLES, accel = Vector3.new(0, 1, 0),
			speed = NumberRange.new(0.5, 1.5), lifetime = NumberRange.new(0.6, 1.2), size = 0.15 },
	},
	venom = { -- gouttes de venin magenta qui suintent + vapeur toxique
		main = { texture = SMOKE, accel = Vector3.new(0, 0.8, 0), speed = 0.3, rot = 60, light = 0.7 },
		extra = { name = "VenomDrops", texture = SPARKLES, accel = Vector3.new(0, -5, 0),
			speed = NumberRange.new(0, 0.4), lifetime = NumberRange.new(0.5, 1), size = 0.1 },
	},
	amber = { -- poussière d'ambre dorée + éclats qui tournoient
		main = { texture = SMOKE, accel = Vector3.new(0, 0.6, 0), speed = 0.3, rot = 40, light = 0.8 },
		extra = { name = "AmberShards", texture = SPARKLES, accel = Vector3.new(0, 1, 0),
			speed = NumberRange.new(0.3, 1), lifetime = NumberRange.new(1, 2), size = 0.14 },
	},
	swarm = { -- nuée de petites étincelles qui grouillent + poussière
		main = { texture = SPARKLES, accel = Vector3.new(0, 0.5, 0), speed = 2, rot = 360, light = 1 },
		extra = { name = "Dust", texture = SMOKE, accel = Vector3.new(0, 0.2, 0),
			speed = NumberRange.new(0.1, 0.4), lifetime = NumberRange.new(1, 2), size = 0.4 },
	},
	hive = { -- gouttes de miel qui tombent + bourdonnement d'étincelles dorées
		main = { texture = SPARKLES, accel = Vector3.new(0, 1, 0), speed = 1.5, rot = 200, light = 1 },
		extra = { name = "Honey", texture = SPARKLES, accel = Vector3.new(0, -4, 0),
			speed = NumberRange.new(0, 0.3), lifetime = NumberRange.new(0.6, 1.2), size = 0.12 },
	},
	necro = { -- âmes violettes qui s'élèvent en spirale + étincelles de chandelle
		main = { texture = SMOKE, accel = Vector3.new(0, 3, 0), speed = 0.8, rot = 240, light = 0.9 },
		extra = { name = "CandleSparks", texture = SPARKLES, accel = Vector3.new(0, 1.5, 0),
			speed = NumberRange.new(0.2, 0.6), lifetime = NumberRange.new(0.8, 1.6), size = 0.1 },
	},
	swamp = { -- brume verte du marécage qui rampe + bulles de poison
		main = { texture = SMOKE, accel = Vector3.new(0, 0.3, 0), speed = 0.3, rot = 20, light = 0.7 },
		extra = { name = "Bubbles", texture = SPARKLES, accel = Vector3.new(0, 2, 0),
			speed = NumberRange.new(0.3, 0.8), lifetime = NumberRange.new(1, 2), size = 0.12 },
	},
	gold = { -- poussière d'or scintillante
		main = { texture = SPARKLES, accel = Vector3.new(0, 1, 0), speed = 0.8, rot = 120, light = 1 },
		extra = { name = "GoldDust", texture = SPARKLES, accel = Vector3.new(0, -1, 0),
			speed = NumberRange.new(1, 2), lifetime = NumberRange.new(1, 2), size = 0.15 },
	},
}
local THEME = THEMES["acid"] or THEMES.fire

-- Réglages des particules selon le nom de l'os FX_ (le premier motif trouvé gagne)
local FX_PRESETS = {
	{ match = "Eye",   rate = 18, size = 0.35, lifetime = 0.5, speed = 1.0 },
	{ match = "Heart", rate = 30, size = 0.9,  lifetime = 0.8, speed = 1.5 },
	{ match = "",      rate = 22, size = 0.6,  lifetime = 0.7, speed = 2.0 }, -- défaut
}

local function presetFor(boneName)
	for _, preset in ipairs(FX_PRESETS) do
		if string.find(boneName, preset.match, 1, true) then
			return preset
		end
	end
end

local function makeFlames(parent, preset)
	local flames = Instance.new("ParticleEmitter")
	flames.Name = "MythicFlames"
	flames.Texture = THEME.main.texture
	flames.Color = ColorSequence.new(GLOW_HOT, GLOW)
	flames.LightEmission = THEME.main.light
	flames.LightInfluence = 0
	flames.Size = NumberSequence.new({
		NumberSequenceKeypoint.new(0, preset.size),
		NumberSequenceKeypoint.new(1, 0),
	})
	flames.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.2),
		NumberSequenceKeypoint.new(1, 1),
	})
	flames.Lifetime = NumberRange.new(preset.lifetime * 0.6, preset.lifetime)
	flames.Rate = preset.rate
	local k = THEME.main.speed
	flames.Speed = NumberRange.new(preset.speed * 0.5 * k, preset.speed * k)
	flames.SpreadAngle = Vector2.new(15, 15)
	flames.Acceleration = THEME.main.accel
	flames.RotSpeed = NumberRange.new(-THEME.main.rot, THEME.main.rot)
	flames.Parent = parent

	local extra = THEME.extra
	local embers = Instance.new("ParticleEmitter")
	embers.Name = "Mythic" .. extra.name
	embers.Texture = extra.texture
	embers.Color = ColorSequence.new(GLOW_HOT)
	embers.LightEmission = 1
	embers.Size = NumberSequence.new(preset.size * extra.size)
	embers.Lifetime = extra.lifetime
	embers.Rate = preset.rate * 0.3
	embers.Speed = extra.speed
	embers.SpreadAngle = Vector2.new(60, 60)
	embers.Acceleration = extra.accel
	embers.Parent = parent
end

local function pulse(light)
	local info = TweenInfo.new(1.2, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true)
	TweenService:Create(light, info, { Brightness = light.Brightness * 0.35 }):Play()
end

for _, inst in ipairs(model:GetDescendants()) do
	if inst:IsA("MeshPart") and string.sub(inst.Name, -5) == "_Glow" then
		inst.Material = Enum.Material.Neon
		inst.TextureID = ""
		inst.Color = GLOW
		inst.CastShadow = false

		local light = Instance.new("PointLight")
		light.Color = GLOW
		light.Brightness = 3
		light.Range = 16
		light.Parent = inst
		pulse(light)
	elseif inst:IsA("Bone") and string.sub(inst.Name, 1, 3) == "FX_" then
		makeFlames(inst, presetFor(inst.Name))
	end
end
