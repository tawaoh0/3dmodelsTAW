--[[
	Effets mythiques — {{NAME}}
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

local GLOW = Color3.fromRGB({{GLOW}})
local GLOW_HOT = Color3.fromRGB({{GLOW_HOT}})

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
	gold = { -- poussière d'or scintillante
		main = { texture = SPARKLES, accel = Vector3.new(0, 1, 0), speed = 0.8, rot = 120, light = 1 },
		extra = { name = "GoldDust", texture = SPARKLES, accel = Vector3.new(0, -1, 0),
			speed = NumberRange.new(1, 2), lifetime = NumberRange.new(1, 2), size = 0.15 },
	},
}
local THEME = THEMES["{{THEME}}"] or THEMES.fire

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
