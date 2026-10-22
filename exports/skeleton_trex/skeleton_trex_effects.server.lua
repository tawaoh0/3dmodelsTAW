--[[
	Effets mythiques — skeleton_trex
	Généré par build.py (3dmodelsTAW).

	Installation : placer ce Script directement dans le Model de la créature
	importée (à côté des MeshParts). Il :
	  • passe les pièces « *_Glow » en matériau Neon de la couleur de lueur ;
	  • ajoute une lumière qui pulse ;
	  • attache des flammes / braises à chaque os nommé « FX_* ».
]]

local TweenService = game:GetService("TweenService")

local model = script.Parent

local GLOW = Color3.fromRGB(255, 36, 24)
local GLOW_HOT = Color3.fromRGB(255, 176, 112)

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
	flames.Texture = "rbxasset://textures/particles/fire_main.dds"
	flames.Color = ColorSequence.new(GLOW_HOT, GLOW)
	flames.LightEmission = 1
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
	flames.Speed = NumberRange.new(preset.speed * 0.5, preset.speed)
	flames.SpreadAngle = Vector2.new(15, 15)
	flames.Acceleration = Vector3.new(0, 4, 0)
	flames.RotSpeed = NumberRange.new(-90, 90)
	flames.Parent = parent

	local embers = Instance.new("ParticleEmitter")
	embers.Name = "MythicEmbers"
	embers.Texture = "rbxasset://textures/particles/sparkles_main.dds"
	embers.Color = ColorSequence.new(GLOW_HOT)
	embers.LightEmission = 1
	embers.Size = NumberSequence.new(preset.size * 0.25)
	embers.Lifetime = NumberRange.new(0.8, 1.6)
	embers.Rate = preset.rate * 0.3
	embers.Speed = NumberRange.new(1, 3)
	embers.SpreadAngle = Vector2.new(60, 60)
	embers.Acceleration = Vector3.new(0, 2, 0)
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
