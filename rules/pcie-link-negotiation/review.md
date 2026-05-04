# PCIe Link Negotiation Rule Pack

Rule pack: `pcie-link-negotiation`

## Rule basis

- Require target-versus-negotiated speed and width evidence.
- Treat downtraining and degraded width as explicit review topics.
- Do not approve silent fallback outcomes.

## Review prompts

- Did the link negotiate the intended Gen5 speed?
- Did width or speed degrade, and if so, was that expected?
- Is fallback reason explicit enough for reviewer sign-off?
