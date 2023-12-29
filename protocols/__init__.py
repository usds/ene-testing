from .usds import USDS
from .mitc import MITC

producers = {
	"USDS": USDS.produce,
	"MITC": MITC.produce,
}

consumers = {
	"USDS": USDS.consume,
	"MITC": MITC.consume,
}
