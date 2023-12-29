from .usds import USDS
from .mitc import MITC

adaptor = {
	"USDS": USDS.adaptor,
	"MITC": MITC.adaptor,
}