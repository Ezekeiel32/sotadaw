/* ------------------------------------------------------------
name: "riser"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Riser -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Riser_H__
#define  __Riser_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Riser
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float Riser_faustpower2_f(float value) {
	return value * value;
}

class Riser : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec0[2];
	FAUSTFLOAT fHslider1;
	int fSampleRate;
	float fConst0;
	float fConst1;
	FAUSTFLOAT fHslider2;
	float fConst2;
	FAUSTFLOAT fHslider3;
	int iRec2[2];
	float fRec1[3];
	FAUSTFLOAT fHslider4;
	
 public:
	Riser() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Riser -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "riser.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "riser");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.08f * fConst0);
		fConst2 = 3.1415927f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(2e+01f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(8.0f);
		fHslider2 = FAUSTFLOAT(3e+02f);
		fHslider3 = FAUSTFLOAT(1.2f);
		fHslider4 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec0[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 3; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual Riser* clone() {
		return new Riser();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("riser");
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(3e+02f), FAUSTFLOAT(5e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("q", &fHslider3, FAUSTFLOAT(1.2f), FAUSTFLOAT(0.5f), FAUSTFLOAT(6.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("range", &fHslider0, FAUSTFLOAT(2e+01f), FAUSTFLOAT(2.0f), FAUSTFLOAT(4e+01f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("sweep", &fHslider1, FAUSTFLOAT(8.0f), FAUSTFLOAT(0.5f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = float(fButton0);
		float fSlow2 = std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow3 = 1.0f / fSlow2;
		float fSlow4 = float(fHslider2);
		float fSlow5 = 1.0f / float(fHslider3);
		float fSlow6 = float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow1;
			iRec0[0] = (fSlow1 > fVec0[1]) + (fSlow1 <= fVec0[1]) * (iRec0[1] + (iRec0[1] > 0));
			float fTemp0 = float(iRec0[0]);
			float fTemp1 = std::max<float>(0.0f, std::min<float>(fSlow3 * fTemp0, fConst1 * (fSlow2 - fTemp0) + 1.0f));
			float fTemp2 = std::tan(fConst2 * std::min<float>(1.6e+04f, fSlow4 * std::pow(fSlow0, fTemp1)));
			float fTemp3 = 1.0f / fTemp2;
			float fTemp4 = (fSlow5 + fTemp3) / fTemp2 + 1.0f;
			iRec2[0] = 1103515245 * iRec2[1] + 12345;
			fRec1[0] = 4.656613e-10f * float(iRec2[0]) - (fRec1[2] * ((fTemp3 - fSlow5) / fTemp2 + 1.0f) + 2.0f * fRec1[1] * (1.0f - 1.0f / Riser_faustpower2_f(fTemp2))) / fTemp4;
			float fTemp5 = tanhf(fSlow6 * (Riser_faustpower2_f(fTemp1) * (fRec1[0] - fRec1[2]) / (fTemp2 * fTemp4)));
			output0[i0] = FAUSTFLOAT(fTemp5);
			output1[i0] = FAUSTFLOAT(fTemp5);
			fVec0[1] = fVec0[0];
			iRec0[1] = iRec0[0];
			iRec2[1] = iRec2[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
		}
	}

};

#endif
